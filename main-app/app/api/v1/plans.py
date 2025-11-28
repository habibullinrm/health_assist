"""
API endpoints для планов лечения
"""
import os
from typing import List
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()

# Директория для сохранения файлов планов
UPLOAD_DIR = Path("uploads/plans")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/load_plan_file", response_model=schemas.PlanFileUpload, status_code=status.HTTP_201_CREATED)
async def load_plan_file(
    file: UploadFile = File(..., description="PDF файл с планом лечения"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузить файл с планом лечения (PDF)

    Args:
        file: PDF файл с планом лечения
        db: Database session
        current_user: Текущий авторизованный пользователь (из middleware)

    Returns:
        Информация о загруженном файле и созданном плане
    """
    # Проверяем, что файл является PDF
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Генерируем уникальное имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"plan_{current_user.id}_{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / file_name

    # Сохраняем файл
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

    # Создаем запись плана в базе данных с автоматически сгенерированными данными
    today = datetime.now().date()

    # Используем имя файла как название плана (убираем расширение)
    title = file.filename.replace('.pdf', '') if file.filename else f"План лечения от {today}"

    plan_data = schemas.PlanCreate(
        title=title,
        description=f"Загружено из Telegram {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        start_date=today,
        end_date=today + timedelta(days=30),  # По умолчанию на месяц
        status="pending",
        share_with_doctor=False,
        original_file_path=str(file_path),  # Сохраняем путь к оригинальному файлу
        doctor_id=1,  # Дефолтный врач (TODO: можно сделать настройку)
        user_id=current_user.id
    )

    plan = await crud.plan.create(db, obj_in=plan_data)
    await db.commit()

    return schemas.PlanFileUpload(
        id=plan.id,
        title=plan.title,
        file_path=str(file_path),
        message="Plan file uploaded successfully"
    )


@router.get("/get_all", response_model=List[schemas.PlanRead])
async def get_all_plans(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить все планы лечения текущего пользователя

    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество записей
        db: Database session
        current_user: Текущий авторизованный пользователь

    Returns:
        Список планов лечения пользователя
    """
    plans = await crud.plan.get_by_user_id(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return plans


@router.get("/get_one/{plan_id}", response_model=schemas.PlanRead)
async def get_one_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить конкретный план лечения пользователя

    Args:
        plan_id: ID плана лечения
        db: Database session
        current_user: Текущий авторизованный пользователь

    Returns:
        План лечения
    """
    plan = await crud.plan.get_user_plan(
        db, user_id=current_user.id, plan_id=plan_id
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or you don't have access to it"
        )

    return plan