#!/usr/bin/env python3
"""
Telegram бот для Health Assist
"""
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
TG_TOKEN = os.getenv('TG_TOKEN')
BOT_NAME = os.getenv('BOT_NAME', 'Health Assist Bot')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    welcome_message = (
        f"Здравствуйте, {user.first_name}!\n\n"
        f"Добро пожаловать в {BOT_NAME}.\n\n"
        "Доступные команды:\n"
        "/auth - Авторизация в системе\n"
        "/plan - Просмотр плана лечения\n"
        "/about - О цифровом ассистенте"
    )
    await update.message.reply_text(welcome_message)


async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /auth - заглушка авторизации"""
    user = update.effective_user
    auth_message = (
        f"✅ Вы авторизованы!\n\n"
        f"Пользователь: {user.first_name}\n"
        f"ID: {user.id}\n\n"
        "Теперь вам доступны все функции ассистента."
    )
    await update.message.reply_text(auth_message)
    logger.info(f"User {user.id} ({user.first_name}) authorized")


async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /plan - фейковый план лечения"""
    plan_message = (
        "📋 Ваш план лечения:\n\n"
        "1️⃣ Прием препарата \"Амоксициллин\" 500мг\n"
        "   • По 1 таблетке 3 раза в день после еды\n"
        "   • Курс: 7 дней\n\n"
        "2️⃣ Физиотерапия\n"
        "   • УВЧ-терапия\n"
        "   • 5 сеансов через день\n"
        "   • Начало: завтра, 10:00\n\n"
        "3️⃣ Лабораторные анализы\n"
        "   • Общий анализ крови\n"
        "   • Биохимия крови\n"
        "   • Запись: 15 ноября, 08:00\n\n"
        "4️⃣ Контрольный осмотр\n"
        "   • Повторный прием у терапевта\n"
        "   • Дата: 20 ноября, 14:30\n\n"
        "💡 Не забудьте отмечать выполненные пункты!"
    )
    await update.message.reply_text(plan_message)
    logger.info(f"User {update.effective_user.id} requested treatment plan")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /about - описание ассистента"""
    about_message = (
        "ℹ️ О цифровом ассистенте\n\n"
        "Health Assist - это ваш персональный помощник в вопросах здоровья. "
        "Мы помогаем пациентам лучше понимать и выполнять план лечения, "
        "анализируем совместимость назначенных лекарств и предупреждаем о возможных взаимодействиях. "
        "Ассистент напомнит о предстоящих обследованиях, поможет подготовиться к ним "
        "и обеспечит, чтобы вы ничего не забыли. Ваше здоровье - наша забота! 💙"
    )
    await update.message.reply_text(about_message)
    logger.info(f"User {update.effective_user.id} requested about info")


def main() -> None:
    """Основная функция бота"""
    if not TG_TOKEN:
        logger.error("TG_TOKEN not found in environment variables!")
        return

    logger.info(f"Starting {BOT_NAME}...")

    # Создаем приложение бота
    application = Application.builder().token(TG_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("auth", auth))
    application.add_handler(CommandHandler("plan", plan))
    application.add_handler(CommandHandler("about", about))

    # Запускаем бота
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()