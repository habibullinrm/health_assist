"""
Модель опросов пациентов по симптомам
"""
from sqlalchemy import Column, Integer, Text, DateTime, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Survey(Base):
    """Опросы пациентов по симптомам"""
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    value = Column(Integer, nullable=False, comment="Оценка от 0 до 10")
    user_answer = Column(Text, nullable=True)
    symptom_id = Column(Integer, ForeignKey("symptoms.id", ondelete="CASCADE"), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("value >= 0 AND value <= 10", name="check_survey_value_range"),
        Index("idx_surveys_symptom_id", "symptom_id"),
    )

    # Relationships
    symptom = relationship("Symptom", back_populates="surveys")