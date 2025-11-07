from fastapi import APIRouter, Depends
from app.config import Settings, get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-sales-crm"
    }


@router.get("/info")
async def app_info(settings: Settings = Depends(get_settings)):
    """Application information"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "llm_model": settings.groq_model
    }