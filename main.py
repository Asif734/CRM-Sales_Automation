from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.routes import health, leads, campaigns

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI-powered Sales Campaign CRM with automated lead scoring and outreach.
    
    ## Features
    * 🤖 AI-powered lead scoring using Groq LLM
    * 👥 Automatic buyer persona identification
    * ✉️ Personalized email generation
    * 📊 Campaign analytics and reporting
    * 📧 Email delivery via MailHog (for testing)
    
    ## Quick Start
    1. Check `/health` to verify the API is running
    2. View leads at `/api/v1/leads`
    3. Run a campaign with `POST /api/v1/campaigns/run`
    4. Check results at http://localhost:8025 (MailHog)
    """
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(leads.router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🚀 AI Sales Campaign CRM API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "mailhog": "http://localhost:8025"
    }