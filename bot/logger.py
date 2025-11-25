import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Настройка логирования в файл и консоль"""
    # Создаем директорию для логов если нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Формат логов
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    # Логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 1. Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # 2. Вывод в файл (ротация по 10МБ, храним 5 файлов)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'bot.log'),
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Убираем шум от библиотек
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    return logger
