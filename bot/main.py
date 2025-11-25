#!/usr/bin/env python3
"""
Telegram бот для Health Assist с кнопочным интерфейсом
"""
import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Загружаем переменные окружения
load_dotenv()

import sys
# from logging.handlers import RotatingFileHandler # Removed as it is in logger.py now

# ... imports ...
from logger import setup_logging

# Загружаем переменные окружения
load_dotenv()

logger = setup_logging()
API_URL = os.getenv('API_URL', 'http://api:8000')
WEB_URL = os.getenv('WEB_URL', 'http://127.0.0.1:8000')

# Получаем токен из переменных окружения
TG_TOKEN = os.getenv('TG_TOKEN')
BOT_NAME = os.getenv('BOT_NAME', 'Health Assist Bot')

# Текст кнопок
BTN_AUTH = "🔐 Авторизация"
BTN_ABOUT = "ℹ️ О приложении"
BTN_ADD_PLAN = "➕ Добавить план лечения"
BTN_MY_TREATMENT = "💊 Мое лечение"
BTN_FEEL_BAD = "🆘 Мне плохо"
BTN_NOTIFICATIONS = "🔔 Уведомления"
BTN_SHOW_WITH_RECOMMENDATIONS = "📋 Показать с рекомендациями"
BTN_DOWNLOAD_PDF = "📄 Скачать PDF"
BTN_BACK = "◀️ Назад"


def get_unauthorized_keyboard():
    """Клавиатура для неавторизованных пользователей"""
    keyboard = [
        [KeyboardButton(BTN_AUTH)],
        [KeyboardButton(BTN_ABOUT)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_main_keyboard():
    """Главное меню для авторизованных пользователей"""
    keyboard = [
        [KeyboardButton(BTN_ADD_PLAN)],
        [KeyboardButton(BTN_MY_TREATMENT)],
        [KeyboardButton(BTN_FEEL_BAD)],
        [KeyboardButton(BTN_NOTIFICATIONS)],
        [KeyboardButton(BTN_ABOUT)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_treatment_submenu():
    """Подменю для 'Мое лечение'"""
    keyboard = [
        [InlineKeyboardButton(BTN_SHOW_WITH_RECOMMENDATIONS, callback_data="treatment_show")],
        [InlineKeyboardButton(BTN_DOWNLOAD_PDF, callback_data="treatment_pdf")],
        [InlineKeyboardButton(BTN_BACK, callback_data="treatment_back")]
    ]
    return InlineKeyboardMarkup(keyboard)


def is_authorized(context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Проверка авторизации пользователя"""
    return context.user_data.get('authorized', False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Автоматически проверяем авторизацию при старте
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/api/v1/auth/check/{user.id}")
            if response.status_code == 200:
                data = response.json()
                # Пользователь авторизован
                was_authorized = context.user_data.get('authorized', False)
                context.user_data['authorized'] = True
                
                if not was_authorized:
                    # Пользователь только что авторизовался
                    auth_message = (
                        f"✅ Вы успешно авторизованы!\n\n"
                        f"Пользователь: {data.get('user')}\n"
                        f"ID: {user.id}\n\n"
                        "Теперь вам доступны все функции ассистента."
                    )
                    await update.message.reply_text(auth_message, reply_markup=get_main_keyboard())
                    logger.info(f"User {user.id} newly authorized")
                    return
            else:
                # Пользователь не найден или не авторизован - сбрасываем флаг
                context.user_data['authorized'] = False
                logger.info(f"User {user.id} not authorized, status code: {response.status_code}")
        except Exception as e:
            # При ошибке также сбрасываем флаг авторизации
            context.user_data['authorized'] = False
            logger.error(f"Error checking auth on start: {e}")

    if is_authorized(context):
        welcome_message = (
            f"Здравствуйте, {user.first_name}! 👋\n\n"
            f"Добро пожаловать в {BOT_NAME}.\n\n"
            "Выберите действие из меню:"
        )
        keyboard = get_main_keyboard()
    else:
        context.user_data['authorized'] = False
        welcome_message = (
            f"Здравствуйте, {user.first_name}! 👋\n\n"
            f"Добро пожаловать в {BOT_NAME}.\n\n"
            "Для начала работы необходимо авторизоваться."
        )
        keyboard = get_unauthorized_keyboard()

    await update.message.reply_text(welcome_message, reply_markup=keyboard)
    logger.info(f"User {user.id} ({user.first_name}) started the bot")


async def handle_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик авторизации"""
    user = update.effective_user
    
    # Check auth status in backend
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/api/v1/auth/check/{user.id}")
            if response.status_code == 200:
                data = response.json()
                # User is authorized
                context.user_data['authorized'] = True
                
                auth_message = (
                    f"✅ Вы успешно авторизованы!\n\n"
                    f"Пользователь: {data.get('user')}\n"
                    f"ID: {user.id}\n\n"
                    "Теперь вам доступны все функции ассистента."
                )
                keyboard = get_main_keyboard()
                if update.callback_query:
                    await update.callback_query.message.reply_text(auth_message, reply_markup=keyboard)
                else:
                    await update.message.reply_text(auth_message, reply_markup=keyboard)
                logger.info(f"User {user.id} authorized via backend check")
                return
        except Exception as e:
            logger.error(f"Error checking auth: {e}")

    # Not authorized or error -> Send link
    auth_url = f"{WEB_URL}/api/v1/auth/login?telegram_id={user.id}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Войти через Яндекс ID", url=auth_url)]
    ])
    
    message_text = (
        "Для работы с ассистентом необходима авторизация.\n\n"
        "Пожалуйста, войдите через Яндекс ID.\n"
        "После авторизации откройте бота снова командой /start"
    )
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(message_text, reply_markup=keyboard)
        except Exception as e:
            # Ignore "Message is not modified" error
            if "Message is not modified" in str(e):
                await update.callback_query.answer("Статус авторизации не изменился")
            else:
                logger.error(f"Error editing message: {e}")
    else:
        await update.message.reply_text(message_text, reply_markup=keyboard)
    
    logger.info(f"User {user.id} sent auth link")


async def handle_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик 'О приложении'"""
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


async def handle_add_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик 'Добавить план лечения'"""
    message = (
        "➕ Добавление плана лечения\n\n"
        "Здесь вы сможете добавить новый план лечения, назначенный вашим врачом.\n\n"
        "🚧 Функция находится в разработке..."
    )
    await update.message.reply_text(message)
    logger.info(f"User {update.effective_user.id} requested add plan")


async def handle_my_treatment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик 'Мое лечение' - показывает подменю"""
    message = "💊 Мое лечение\n\nВыберите действие:"
    keyboard = get_treatment_submenu()
    await update.message.reply_text(message, reply_markup=keyboard)
    logger.info(f"User {update.effective_user.id} opened treatment menu")


async def handle_feel_bad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик 'Мне плохо'"""
    message = (
        "🆘 Экстренная помощь\n\n"
        "Если вам требуется срочная медицинская помощь, "
        "немедленно обратитесь к врачу или позвоните по номеру экстренной службы:\n\n"
        "📞 103 - Скорая помощь\n"
        "📞 112 - Единый номер экстренных служб\n\n"
        "Опишите ваши симптомы, и я постараюсь дать рекомендации:\n\n"
        "🚧 Функция находится в разработке..."
    )
    await update.message.reply_text(message)
    logger.info(f"User {update.effective_user.id} pressed 'Feel bad' button")


async def handle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик 'Уведомления'"""
    message = (
        "🔔 Уведомления\n\n"
        "Здесь будут отображаться напоминания о:\n"
        "• Приеме лекарств\n"
        "• Предстоящих обследованиях\n"
        "• Записях к врачу\n"
        "• Других важных событиях\n\n"
        "🚧 Функция находится в разработке..."
    )
    await update.message.reply_text(message)
    logger.info(f"User {update.effective_user.id} requested notifications")


async def handle_treatment_show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик 'Показать с рекомендациями'"""
    query = update.callback_query
    await query.answer()

    plan_message = (
        "📋 Ваш план лечения с рекомендациями:\n\n"
        "1️⃣ Прием препарата \"Амоксициллин\" 500мг\n"
        "   • По 1 таблетке 3 раза в день после еды\n"
        "   • Курс: 7 дней\n"
        "   💡 Рекомендация: Запивайте большим количеством воды\n\n"
        "2️⃣ Физиотерапия\n"
        "   • УВЧ-терапия\n"
        "   • 5 сеансов через день\n"
        "   • Начало: завтра, 10:00\n"
        "   💡 Рекомендация: Приходите в свободной одежде\n\n"
        "3️⃣ Лабораторные анализы\n"
        "   • Общий анализ крови\n"
        "   • Биохимия крови\n"
        "   • Запись: 15 ноября, 08:00\n"
        "   💡 Рекомендация: Сдавать натощак (8-12 часов голода)\n\n"
        "4️⃣ Контрольный осмотр\n"
        "   • Повторный прием у терапевта\n"
        "   • Дата: 20 ноября, 14:30\n"
        "   💡 Рекомендация: Возьмите с собой результаты анализов\n\n"
        "✅ Не забывайте отмечать выполненные пункты!"
    )
    await query.edit_message_text(plan_message)
    logger.info(f"User {query.from_user.id} requested treatment plan with recommendations")


async def handle_treatment_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик 'Скачать PDF'"""
    query = update.callback_query
    await query.answer()

    message = (
        "📄 Скачать план лечения в PDF\n\n"
        "Здесь вы сможете скачать ваш план лечения в формате PDF для печати или хранения.\n\n"
        "🚧 Функция находится в разработке..."
    )
    await query.edit_message_text(message)
    logger.info(f"User {query.from_user.id} requested PDF download")


async def handle_treatment_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик 'Назад' из подменю лечения"""
    query = update.callback_query
    await query.answer()

    message = "Главное меню. Выберите действие:"
    await query.edit_message_text(message)
    logger.info(f"User {query.from_user.id} returned to main menu")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback-запросов от inline кнопок"""
    query = update.callback_query

    handlers = {
        "treatment_show": handle_treatment_show,
        "treatment_pdf": handle_treatment_pdf,
        "treatment_back": handle_treatment_back,
    }

    handler = handlers.get(query.data)
    if handler:
        await handler(update, context)
    else:
        await query.answer("Неизвестная команда")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений (нажатий на кнопки)"""
    text = update.message.text

    # Маршрутизация по тексту кнопки
    if text == BTN_AUTH:
        await handle_auth(update, context)
    elif text == BTN_ABOUT:
        await handle_about(update, context)
    elif text == BTN_ADD_PLAN:
        if not is_authorized(context):
            await update.message.reply_text("⚠️ Сначала необходимо авторизоваться!")
            return
        await handle_add_plan(update, context)
    elif text == BTN_MY_TREATMENT:
        if not is_authorized(context):
            await update.message.reply_text("⚠️ Сначала необходимо авторизоваться!")
            return
        await handle_my_treatment(update, context)
    elif text == BTN_FEEL_BAD:
        if not is_authorized(context):
            await update.message.reply_text("⚠️ Сначала необходимо авторизоваться!")
            return
        await handle_feel_bad(update, context)
    elif text == BTN_NOTIFICATIONS:
        if not is_authorized(context):
            await update.message.reply_text("⚠️ Сначала необходимо авторизоваться!")
            return
        await handle_notifications(update, context)
    else:
        await update.message.reply_text(
            "Я вас не понял. Пожалуйста, используйте кнопки меню."
        )


def main() -> None:
    """Основная функция бота"""
    if not TG_TOKEN:
        logger.error("TG_TOKEN not found in environment variables!")
        return

    logger.info(f"Starting {BOT_NAME}...")

    # Создаем приложение бота
    application = Application.builder().token(TG_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()