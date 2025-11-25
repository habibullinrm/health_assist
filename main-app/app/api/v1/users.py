"""
API endpoints для пользователей
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/users", response_model=List[schemas.UserRead])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список пользователей

    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество записей
        db: Database session
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.UserReadWithRole)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить пользователя по ID

    Args:
        user_id: ID пользователя
        db: Database session
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать нового пользователя

    Args:
        user_in: Данные пользователя
        db: Database session
    """
    # Проверяем, не существует ли пользователь с таким external_id
    existing_user = await crud.user.get_by_external_id(db, external_id=user_in.external_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this external_id already exists"
        )

    # Проверяем, не существует ли пользователь с таким phone
    existing_phone = await crud.user.get_by_phone(db, phone=user_in.phone)
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone already exists"
        )

    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.patch("/users/{user_id}", response_model=schemas.UserRead)
async def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить данные пользователя

    Args:
        user_id: ID пользователя
        user_in: Обновленные данные
        db: Database session
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить пользователя

    Args:
        user_id: ID пользователя
        db: Database session
    """
    user = await crud.user.delete(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None