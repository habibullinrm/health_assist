#!/usr/bin/env python3
"""
Sber Mock Service
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Sber Mock Service",
    description="Мок-сервис для имитации работы Сбер-здоровья",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Main endpoint"""
    return {
        "service": "Sber Mock Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/test")
async def test():
    """Test endpoint"""
    return {
        "service": "Sber Mock Service",
        "message": "Mock service is working correctly"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sber Mock Service"
    }