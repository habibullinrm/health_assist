#!/usr/bin/env python3
"""
Health Assist API - главная точка входа
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Главный API цифрового ассистента пациента",
    version=settings.APP_VERSION,
    debug=settings.APP_DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.APP_ENV}")


@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    print("Shutting down...")


@app.get("/")
async def root():
    """Main endpoint"""
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
    }


# Подключение роутов API v1
from app.api.v1 import auth, users, plans

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(plans.router, prefix="/api/v1/plans", tags=["plans"])