"""
Базовая модель для всех SQLAlchemy моделей
"""
from app.core.database import Base

# Экспортируем Base для использования в других моделях
__all__ = ["Base"]