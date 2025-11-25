"""
SQLAlchemy модели
"""
from app.models.base import Base
from app.models.user import Role, User
from app.models.doctor import Doctor
from app.models.medicin import Medicin
from app.models.plan import Plan
from app.models.appointment import Appointment
from app.models.prescription import MedicalPrescription
from app.models.test import MedicalTest
from app.models.symptom import Symptom
from app.models.survey import Survey
from app.models.notification import Notification

# Все модели должны быть импортированы здесь для Alembic autogenerate

__all__ = [
    "Base",
    "Role",
    "User",
    "Doctor",
    "Medicin",
    "Plan",
    "Appointment",
    "MedicalPrescription",
    "MedicalTest",
    "Symptom",
    "Survey",
    "Notification",
]