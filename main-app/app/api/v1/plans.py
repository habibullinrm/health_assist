"""
API endpoints для планов лечения
"""
import os
import logging
from typing import List
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.pdf_processor import process_treatment_plan_pdf
from app.services.gigachat_service import get_gigachat_service
from app.prompts import load_treatment_plan_prompt

# Настройка логирования
logger = logging.getLogger(__name__)

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

    # Обрабатываем PDF-файл и извлекаем текст
    logger.info(f"Начало обработки PDF-файла: {file_path}")
    pdf_result = process_treatment_plan_pdf(str(file_path))

    logger.info(f"Статус обработки PDF: {pdf_result['status']}")
    logger.info(f"Сообщение: {pdf_result['message']}")

    if pdf_result['status'] == 'success':
        logger.info(f"Тип PDF: {pdf_result['data'].get('pdf_type')}")
        logger.info(f"Количество символов в тексте: {pdf_result['data'].get('text_length')}")
        logger.info(f"Метаданные: {pdf_result['data'].get('metadata')}")
        logger.info(f"Извлеченный текст:\n{pdf_result['data'].get('text')}")

        # Извлекаем структурированную информацию с помощью GigaChat
        extracted_text = pdf_result['data'].get('text')

        try:
            logger.info("=" * 80)
            logger.info("Начало извлечения структурированной информации с помощью GigaChat")
            logger.info("=" * 80)

            # Загружаем промпт
            system_prompt, user_prompt, llm_params = load_treatment_plan_prompt(extracted_text)

            logger.info(f"Системный промпт загружен (длина: {len(system_prompt)} символов)")
            logger.info(f"Пользовательский промпт сформирован (длина: {len(user_prompt)} символов)")
            logger.info(f"Параметры LLM: {llm_params}")

            # Инициализируем GigaChat и отправляем запрос
            with get_gigachat_service() as giga:
                logger.info("GigaChat сервис инициализирован")

                # Формируем сообщения
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

                logger.info("Отправка запроса к GigaChat API...")

                # Отправляем запрос
                gigachat_response = giga.chat(
                    messages=messages,
                    temperature=llm_params.get('temperature', 0.1),
                    max_tokens=llm_params.get('max_tokens', 2000),
                    top_p=llm_params.get('top_p', 0.95)
                )

                logger.info("=" * 80)
                logger.info("ОТВЕТ ОТ GIGACHAT:")
                logger.info("=" * 80)
                logger.info(gigachat_response)
                logger.info("=" * 80)
                logger.info(f"Длина ответа: {len(gigachat_response)} символов")

                # Попытка распарсить JSON
                import json
                try:
                    # Очищаем ответ от markdown если есть
                    cleaned_response = gigachat_response.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:]
                    if cleaned_response.startswith("```"):
                        cleaned_response = cleaned_response[3:]
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]
                    cleaned_response = cleaned_response.strip()

                    parsed_response = json.loads(cleaned_response)
                    logger.info("=" * 80)
                    logger.info("СТРУКТУРИРОВАННЫЕ ДАННЫЕ:")
                    logger.info("=" * 80)
                    logger.info(json.dumps(parsed_response, indent=2, ensure_ascii=False))
                    logger.info("=" * 80)

                    # Логируем ключевые данные
                    if 'doctor' in parsed_response:
                        logger.info(f"Врач: {parsed_response['doctor']}")
                    if 'symptoms' in parsed_response:
                        logger.info(f"Симптомов: {len(parsed_response['symptoms'])}")
                    if 'medications' in parsed_response:
                        logger.info(f"Лекарств назначено: {len(parsed_response['medications'])}")
                    if 'examinations' in parsed_response:
                        logger.info(f"Обследований: {len(parsed_response['examinations'])}")
                    if 'referrals' in parsed_response:
                        logger.info(f"Направлений к врачам: {len(parsed_response['referrals'])}")

                except json.JSONDecodeError as e:
                    logger.warning(f"Не удалось распарсить ответ как JSON: {e}")
                    logger.warning("Ответ будет обработан как текст")

        except Exception as e:
            logger.error(f"Ошибка при работе с GigaChat: {e}", exc_info=True)
            logger.warning("Продолжаем без извлечения структурированной информации")

    elif pdf_result['status'] == 'error':
        logger.warning(f"Ошибка обработки PDF: {pdf_result['message']}")
        if 'data' in pdf_result:
            logger.info(f"Дополнительные данные: {pdf_result['data']}")

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

    # временно закомментил, надо бд поправить
    # plan = await crud.plan.create(db, obj_in=plan_data)
    # await db.commit()

    return schemas.PlanFileUpload(
        id=1, #plan.id,
        title=title, #plan.title,
        file_path=str(file_path),
        message=str(pdf_result['data'])
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