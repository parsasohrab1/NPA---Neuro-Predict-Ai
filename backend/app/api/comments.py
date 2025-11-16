"""
Comments API - lightweight collaboration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..db.session import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.communication import Comment

router = APIRouter(prefix="/comments", tags=["Comments"])


class CommentCreate(BaseModel):
    entity_type: str = Field(..., min_length=2, max_length=64)
    entity_id: int
    body: str = Field(..., min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    author_id: int
    body: str

    class Config:
        from_attributes = True


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = Comment(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        author_id=current_user.id,
        body=payload.body,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("", response_model=List[CommentResponse])
async def list_comments(
    entity_type: str = Query(..., min_length=2, max_length=64),
    entity_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Comment).where(Comment.entity_type == entity_type, Comment.entity_id == entity_id).order_by(Comment.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only author (or admin in future) can delete
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if item.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    await db.execute(delete(Comment).where(Comment.id == comment_id))
    await db.commit()
    return None


