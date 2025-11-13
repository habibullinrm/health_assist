#!/usr/bin/env python3
"""
Health Assist API
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Health Assist API",
    description="Главный api цифрового ассистента пациента",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Main endpoint"""
    return {
        "service": "Health Assist API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/test")
async def test():
    """"Тестовый get запрос"""
    return {
        "service": "Health Assist API",
        "message": "API is working correctly"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Health Assist API"
    }