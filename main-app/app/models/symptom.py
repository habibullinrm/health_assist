"""
Модель симптомов пациентов
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Symptom(Base):
    """Симптомы пациентов"""
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Constraints
    __table_args__ = (
        Index("idx_symptoms_plan_id", "plan_id"),
    )

    # Relationships
    plan = relationship("Plan", back_populates="symptoms")
    surveys = relationship("Survey", back_populates="symptom", cascade="all, delete-orphan")