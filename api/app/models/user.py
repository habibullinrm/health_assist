"""
Модель пользователя
"""
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Role(Base):
    """Роли пользователей"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(32), nullable=False, unique=True)

    # Relationships
    users = relationship("User", back_populates="role")


class User(Base):
    """Пользователи системы"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    sex = Column(
        String(10),
        nullable=False,
        comment="male, female, other"
    )
    age = Column(Integer, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("sex IN ('male', 'female', 'other')", name="check_sex"),
        CheckConstraint("age >= 0 AND age <= 150", name="check_age"),
    )

    # Relationships
    role = relationship("Role", back_populates="users")
    plans = relationship("Plan", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")