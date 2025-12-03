"""
Настройки приложения
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения из переменных окружения.

    Docker Compose передаёт переменные из обоих .env файлов:
    - Корневой .env (общие переменные для всех сервисов)
    - main-app/.env (API-специфичные переменные)
    """

    # Основные настройки (из main-app/.env)
    APP_NAME: str
    APP_VERSION: str
    APP_ENV: str
    APP_DEBUG: bool

    # База данных (из корневого .env)
    DB_CONNECTION: str
    DB_HOST: str
    DB_PORT: int
    DB_DATABASE: str
    DB_USERNAME: str
    DB_PASSWORD: str

    # GigaChat (из main-app/.env)
    GC_CLIENT_ID: str
    GC_SCOPE: str
    GC_AUTH_KEY: str
    GC_CLIENT_SECRET: str
    GIGACHAT_BASE_URL: Optional[str] = None  # Опционально, если не указано - используется реальный API GigaChat

    # Yandex OAuth (из main-app/.env)
    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    YANDEX_REDIRECT_URI: str

    # Telegram Bot (из main-app/.env)
    BOT_USERNAME: str

    # API URLs (из корневого .env)
    API_URL: str
    WEB_URL: str = ""

    @property
    def DATABASE_URL(self) -> str:
        """Async PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Sync PostgreSQL connection URL (для Alembic миграций)"""
        return f"postgresql+psycopg2://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    class Config:
        # Docker Compose передаёт переменные в окружение контейнера
        # Не нужно явно указывать env_file
        case_sensitive = True
        extra = "ignore"


# Глобальный экземпляр настроек
settings = Settings()