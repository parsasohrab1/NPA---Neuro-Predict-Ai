"""
Product Schemas
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
	name: str = Field(..., min_length=1)
	version: Optional[str] = None
	description: Optional[str] = None
	specs: Optional[Dict[str, Any]] = None
	metadata: Optional[Dict[str, Any]] = None
	is_active: bool = True


class ProductCreate(ProductBase):
	pass


class ProductUpdate(BaseModel):
	name: Optional[str] = None
	version: Optional[str] = None
	description: Optional[str] = None
	specs: Optional[Dict[str, Any]] = None
	metadata: Optional[Dict[str, Any]] = None
	is_active: Optional[bool] = None


class ProductResponse(ProductBase):
	id: int
	created_at: datetime
	updated_at: Optional[datetime] = None
	
	class Config:
		from_attributes = True


