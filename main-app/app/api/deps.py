"""
Зависимости для FastAPI endpoints
"""
from typing import AsyncGenerator

from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db as get_db_session
from app.models.user import User

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


async def get_current_user(
    x_telegram_id: str = Header(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Зависимость для проверки авторизации пользователя
    
    Проверяет:
    - Существует ли пользователь с указанным telegram_id
    - Авторизован ли пользователь (наличие yandex_id)
    
    Args:
        x_telegram_id: Telegram ID пользователя из заголовка X-Telegram-ID
        db: Database session
        
    Returns:
        User: Авторизованный пользователь
        
    Raises:
        HTTPException: 401 если пользователь не найден или не авторизован
        
    Использование:
    ```python
    @router.get("/users")
    async def get_users(current_user: User = Depends(get_current_user)):
        ...
    ```
    """
    # Ищем пользователя по telegram_id (external_id)
    query = select(User).where(User.external_id == x_telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please authorize first."
        )
    
    # Проверяем, что пользователь авторизован через Yandex
    if not user.yandex_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized. Please complete Yandex ID authorization."
        )
    
    return user