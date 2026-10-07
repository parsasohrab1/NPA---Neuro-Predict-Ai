"""
User Schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from ..models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole = UserRole.VIEWER
    license_number: Optional[str] = None
    department: Optional[str] = None
    institution: Optional[str] = None


_COMMON_PASSWORDS = frozenset({
    "password", "password1", "password123", "12345678", "123456789", "1234567890",
    "qwerty123", "qwertyuiop", "iloveyou", "admin123", "letmein1", "welcome1",
})


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def _reject_weak_password(cls, value: str) -> str:
        if value.isdigit():
            raise ValueError("Password must not consist of digits only")
        if value.lower() in _COMMON_PASSWORDS:
            raise ValueError("Password is too common")
        return value


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    license_number: Optional[str] = None
    department: Optional[str] = None
    institution: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None

