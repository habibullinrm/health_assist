"""
Модель медицинских назначений (рецептов)
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class MedicalPrescription(Base):
    """Медицинские назначения (рецепты)"""
    __tablename__ = "medical_prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    dosage = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    description = Column(Text, nullable=True)
    status = Column(
        String(50),
        nullable=False,
        comment="active, completed, cancelled, expired"
    )
    repeat = Column(String(100), nullable=False, comment="Частота приёма")
    medicin_id = Column(Integer, ForeignKey("medicins.id", ondelete="RESTRICT"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("dosage > 0", name="check_dosage_positive"),
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("duration_days > 0", name="check_duration_positive"),
        CheckConstraint(
            "status IN ('active', 'completed', 'cancelled', 'expired')",
            name="check_prescription_status"
        ),
        Index("idx_medical_prescriptions_plan_id", "plan_id"),
        Index("idx_medical_prescriptions_medicin_id", "medicin_id"),
    )

    # Relationships
    medicin = relationship("Medicin", back_populates="prescriptions")
    plan = relationship("Plan", back_populates="prescriptions")