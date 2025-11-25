"""
Модель записей на приём к врачу
"""
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import Base


class Appointment(Base):
    """Записи на приём к врачу"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_specialization = Column(String(100), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        String(50),
        nullable=False,
        comment="scheduled, completed, cancelled, missed"
    )
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled', 'missed')",
            name="check_appointment_status"
        ),
        Index("idx_appointments_plan_id", "plan_id"),
    )

    # Relationships
    plan = relationship("Plan", back_populates="appointments")