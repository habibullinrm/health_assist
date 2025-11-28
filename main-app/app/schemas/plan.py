"""
Pydantic схемы для Plan
"""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    """Базовая схема плана лечения"""
    title: str = Field(..., max_length=255)
    description: str
    start_date: date
    end_date: date
    status: Literal["active", "completed", "cancelled", "pending"] = "pending"
    share_with_doctor: bool = False
    original_file_path: Optional[str] = Field(None, max_length=500)
    doctor_id: int


class PlanCreate(PlanBase):
    """Схема для создания плана лечения"""
    user_id: int


class PlanUpdate(BaseModel):
    """Схема для обновления плана лечения"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[Literal["active", "completed", "cancelled", "pending"]] = None
    share_with_doctor: Optional[bool] = None
    original_file_path: Optional[str] = Field(None, max_length=500)
    doctor_id: Optional[int] = None


class PlanRead(PlanBase):
    """Схема для чтения плана лечения"""
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PlanFileUpload(BaseModel):
    """Схема для ответа после загрузки файла плана"""
    id: int
    title: str
    file_path: str
    message: str

    model_config = {"from_attributes": True}