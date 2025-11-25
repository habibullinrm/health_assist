"""
Модель лекарственных препаратов
"""
from sqlalchemy import Column, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from app.models.base import Base


class Medicin(Base):
    """Справочник лекарственных препаратов"""
    __tablename__ = "medicins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    international_name = Column(String(255), nullable=False)
    form = Column(String(100), nullable=False, comment="Форма выпуска")
    atc_code = Column(String(20), nullable=False, comment="АТХ код")
    instruction = Column(Text, nullable=False, comment="Инструкция по применению")

    # Relationships
    prescriptions = relationship("MedicalPrescription", back_populates="medicin")

    __table_args__ = (
        Index("idx_medicins_atc_code", "atc_code"),
    )