"""
Настройки приложения
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""

    # Основные настройки
    APP_NAME: str = "Health Assist API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "local"
    APP_DEBUG: bool = True

    # База данных
    DB_CONNECTION: str = "pgsql"
    DB_HOST: str = "pgsql"
    DB_PORT: int = 5432
    DB_DATABASE: str = "main_db"
    DB_USERNAME: str = "root"
    DB_PASSWORD: str = "password"

    # GigaChat
    GC_CLIENT_ID: str = ""
    GC_SCOPE: str = "GIGACHAT_API_CORP"
    GC_AUTH_KEY: str = ""
    GC_CLIENT_SECRET: str = ""
    GIGACHAT_API_KEY: str = ""
    GIGACHAT_BASE_URL: str = "http://sber_mock:8002"

    # Yandex OAuth
    YANDEX_CLIENT_ID: str = ""
    YANDEX_CLIENT_SECRET: str = ""
    YANDEX_REDIRECT_URI: str = "http://localhost:8000/auth/yandex/callback"

    # API
    API_URL: str = "http://localhost:8000"

    @property
    def DATABASE_URL(self) -> str:
        """Async PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Sync PostgreSQL connection URL (для Alembic миграций)"""
        return f"postgresql+psycopg2://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Игнорировать дополнительные поля из .env


# Глобальный экземпляр настроек
settings = Settings()