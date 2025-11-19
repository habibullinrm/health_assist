"""
Зависимости для FastAPI endpoints
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db as get_db_session

# Экспортируем get_db для использования в роутах
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения database сессии

    Использование:
    ```python
    @router.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        ...
    ```
    """
    async for session in get_db_session():
        yield session