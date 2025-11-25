"""
Pydantic схемы для User
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# Схемы для Role
class RoleBase(BaseModel):
    """Базовая схема роли"""
    type: str = Field(..., max_length=32)


class RoleCreate(RoleBase):
    """Схема для создания роли"""
    pass


class RoleRead(RoleBase):
    """Схема для чтения роли"""
    id: int

    model_config = {"from_attributes": True}


# Схемы для User
class UserBase(BaseModel):
    """Базовая схема пользователя"""
    external_id: str = Field(..., max_length=100)
    sex: Optional[Literal["male", "female", "other"]] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    full_name: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    role_id: int

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Валидация номера телефона"""
        # Простая валидация, можно расширить
        if not v.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError("Phone must contain only digits, spaces, + and -")
        return v


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    sex: Optional[Literal["male", "female", "other"]] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role_id: Optional[int] = None


class UserRead(UserBase):
    """Схема для чтения пользователя"""
    id: int
    created_at: datetime
    role_id: int

    model_config = {"from_attributes": True}


class UserReadWithRole(UserRead):
    """Схема для чтения пользователя с ролью"""
    role: RoleRead

    model_config = {"from_attributes": True}