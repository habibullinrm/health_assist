"""
Модель уведомлений для пользователей
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Notification(Base):
    """Уведомления для пользователей"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(
        String(50),
        nullable=False,
        comment="appointment, prescription, test, reminder, alert"
    )
    time = Column(DateTime(timezone=True), nullable=False, comment="Время отправки уведомления")
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, nullable=False, server_default="false")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    medical_entity_id = Column(
        Integer,
        nullable=True,
        comment="ID связанной сущности (appointment/prescription/test)"
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('appointment', 'prescription', 'test', 'reminder', 'alert')",
            name="check_notification_type"
        ),
        Index("idx_notifications_user_id", "user_id"),
    )

    # Relationships
    user = relationship("User", back_populates="notifications")