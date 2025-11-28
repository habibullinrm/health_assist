"""
CRUD операции для Plan
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate


class CRUDPlan(CRUDBase[Plan, PlanCreate, PlanUpdate]):
    """CRUD операции для модели Plan"""

    async def get_by_user_id(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Plan]:
        """Получить все планы лечения пользователя"""
        result = await db.execute(
            select(Plan)
            .where(Plan.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Plan.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_plan(
        self, db: AsyncSession, *, user_id: int, plan_id: int
    ) -> Optional[Plan]:
        """Получить конкретный план лечения пользователя"""
        result = await db.execute(
            select(Plan).where(Plan.id == plan_id, Plan.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_active_plans(
        self, db: AsyncSession, *, user_id: int
    ) -> List[Plan]:
        """Получить активные планы лечения пользователя"""
        result = await db.execute(
            select(Plan)
            .where(Plan.user_id == user_id, Plan.status == "active")
            .order_by(Plan.start_date.desc())
        )
        return list(result.scalars().all())


# Создаем глобальный экземпляр для использования в endpoints
plan = CRUDPlan(Plan)