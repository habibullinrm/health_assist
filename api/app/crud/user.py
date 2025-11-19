"""
CRUD операции для User
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD операции для модели User"""

    async def get_by_external_id(
        self, db: AsyncSession, *, external_id: str
    ) -> Optional[User]:
        """Получить пользователя по external_id"""
        result = await db.execute(
            select(User).where(User.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(
        self, db: AsyncSession, *, phone: str
    ) -> Optional[User]:
        """Получить пользователя по номеру телефона"""
        result = await db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()


# Создаем глобальный экземпляр для использования в endpoints
user = CRUDUser(User)