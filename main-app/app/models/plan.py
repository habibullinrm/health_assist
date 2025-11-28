"""
Модель планов лечения
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Plan(Base):
    """Планы лечения пациентов"""
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(
        String(50),
        nullable=False,
        comment="active, completed, cancelled, pending"
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    share_with_doctor = Column(Boolean, nullable=False, server_default="false")
    original_file_path = Column(String(500), nullable=True, comment="Путь к оригинальному PDF файлу")
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'cancelled', 'pending')",
            name="check_plan_status"
        ),
        Index("idx_plans_user_id", "user_id"),
        Index("idx_plans_doctor_id", "doctor_id"),
    )

    # Relationships
    doctor = relationship("Doctor", back_populates="plans")
    user = relationship("User", back_populates="plans")
    appointments = relationship("Appointment", back_populates="plan", cascade="all, delete-orphan")
    prescriptions = relationship("MedicalPrescription", back_populates="plan", cascade="all, delete-orphan")
    tests = relationship("MedicalTest", back_populates="plan", cascade="all, delete-orphan")
    symptoms = relationship("Symptom", back_populates="plan", cascade="all, delete-orphan")