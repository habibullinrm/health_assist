"""
Модель врачей
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Doctor(Base):
    """Справочник врачей"""
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    specialization = Column(String(100), nullable=False)

    # Relationships
    plans = relationship("Plan", back_populates="doctor")