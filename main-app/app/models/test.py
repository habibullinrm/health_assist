"""
Модель медицинских анализов и обследований
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import Base


class MedicalTest(Base):
    """Медицинские анализы и обследования"""
    __tablename__ = "medical_tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        String(50),
        nullable=False,
        comment="scheduled, completed, cancelled, pending_results"
    )
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled', 'pending_results')",
            name="check_test_status"
        ),
        Index("idx_medical_tests_plan_id", "plan_id"),
    )

    # Relationships
    plan = relationship("Plan", back_populates="tests")