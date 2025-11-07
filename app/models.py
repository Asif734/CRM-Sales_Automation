from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class Lead(BaseModel):
    """Lead data model"""
    
    # Original data
    name: str
    email: EmailStr
    company: str
    role: str
    industry: str
    company_size: str
    website: Optional[str] = None
    
    # AI-generated fields
    ai_persona: Optional[str] = None
    priority: Optional[str] = None
    priority_score: Optional[int] = Field(None, ge=1, le=10)
    enrichment_notes: Optional[str] = None
    
    # Email fields
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    email_sent_at: Optional[datetime] = None
    email_status: Optional[str] = "pending"


class ScoringResult(BaseModel):
    """Lead scoring result"""
    priority: str
    score: int = Field(..., ge=1, le=10)
    reasoning: str


class EnrichmentResult(BaseModel):
    """Lead enrichment result"""
    persona: str
    notes: str
    suggested_approach: str


class EmailDraft(BaseModel):
    """Email draft"""
    subject: str
    body: str
    personalization_notes: str


class CampaignStats(BaseModel):
    """Campaign statistics"""
    total_leads: int
    emails_sent: int
    emails_failed: int
    high_priority: int
    medium_priority: int
    low_priority: int
    top_personas: dict
    top_industries: dict


class CampaignRequest(BaseModel):
    """Request to run a campaign"""
    send_emails: bool = True


class CampaignResponse(BaseModel):
    """Campaign execution response"""
    status: str
    message: str
    leads_processed: int
    emails_sent: int
    report_path: str
    execution_time: float