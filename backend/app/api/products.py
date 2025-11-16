"""
Product Management API Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.session import get_db
from ..models.user import User
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse
from ..core.security import get_current_user, require_role
from ..core.cache import generate_cache_key, get_cached_response, set_cached_response, invalidate_product_cache

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
	product_data: ProductCreate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(require_role("admin"))
):
	"""Create a new product (requires admin role)"""
	new_product = Product(**product_data.model_dump())
	db.add(new_product)
	await db.commit()
	await db.refresh(new_product)
	# Invalidate caches
	await invalidate_product_cache(new_product.id)
	return new_product


@router.get("/", response_model=List[ProductResponse])
async def list_products(
	request: Request,
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=1000),
	search: Optional[str] = None,
	is_active: Optional[bool] = None,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""List products with pagination (cached for 5 minutes)"""
	cache_key = generate_cache_key(
		"products",
		request=request,
		current_user=current_user,
		skip=skip,
		limit=limit,
		search=search,
		is_active=is_active,
	)
	cached = await get_cached_response(cache_key, expire_seconds=300)
	if cached is not None:
		return cached
	
	query = select(Product)
	if search:
		like = f"%{search}%"
		query = query.where((Product.name.ilike(like)) | (Product.description.ilike(like)))
	if is_active is not None:
		query = query.where(Product.is_active == is_active)
	query = query.offset(skip).limit(limit)
	
	result = await db.execute(query)
	products = result.scalars().all()
	await set_cached_response(cache_key, products, expire_seconds=300)
	return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
	request: Request,
	product_id: int,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_user)
):
	"""Get a product by ID (cached for 10 minutes)"""
	cache_key = generate_cache_key(
		"product",
		request=request,
		current_user=current_user,
		product_id=product_id,
	)
	cached = await get_cached_response(cache_key, expire_seconds=600)
	if cached is not None:
		return cached
	
	result = await db.execute(select(Product).where(Product.id == product_id))
	product = result.scalar_one_or_none()
	if not product:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
	
	await set_cached_response(cache_key, product, expire_seconds=600)
	return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
	product_id: int,
	product_data: ProductUpdate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(require_role("admin"))
):
	"""Update product (requires admin role)"""
	result = await db.execute(select(Product).where(Product.id == product_id))
	product = result.scalar_one_or_none()
	if not product:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
	
	update_data = product_data.model_dump(exclude_unset=True)
	for field, value in update_data.items():
		setattr(product, field, value)
	
	await db.commit()
	await db.refresh(product)
	# Invalidate caches
	await invalidate_product_cache(product.id)
	return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
	product_id: int,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(require_role("admin"))
):
	"""Delete product (requires admin role)"""
	result = await db.execute(select(Product).where(Product.id == product_id))
	product = result.scalar_one_or_none()
	if not product:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
	
	await db.delete(product)
	await db.commit()
	# Invalidate caches
	await invalidate_product_cache(product_id=product_id)
	return None


