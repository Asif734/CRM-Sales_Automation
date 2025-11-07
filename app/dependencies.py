from typing import Annotated
from fastapi import Depends
from app.config import get_settings, Settings
from app.utils.llm_client import LLMClient
from app.agents.scoring_agent import ScoringAgent
from app.agents.enrichment_agent import EnrichmentAgent
from app.agents.outreach_agents import OutreachAgent
from app.services.leads_services import LeadService
from app.services.email_services import EmailService
from app.services.report_services import ReportService


def get_llm_client(settings: Annotated[Settings, Depends(get_settings)]) -> LLMClient:
    """Get LLM client instance"""
    return LLMClient(settings)


def get_scoring_agent(llm: Annotated[LLMClient, Depends(get_llm_client)]) -> ScoringAgent:
    """Get scoring agent instance"""
    return ScoringAgent(llm)


def get_enrichment_agent(llm: Annotated[LLMClient, Depends(get_llm_client)]) -> EnrichmentAgent:
    """Get enrichment agent instance"""
    return EnrichmentAgent(llm)


def get_outreach_agent(llm: Annotated[LLMClient, Depends(get_llm_client)]) -> OutreachAgent:
    """Get outreach agent instance"""
    return OutreachAgent(llm)


def get_lead_service(settings: Annotated[Settings, Depends(get_settings)]) -> LeadService:
    """Get lead service instance"""
    return LeadService(settings)


def get_email_service(settings: Annotated[Settings, Depends(get_settings)]) -> EmailService:
    """Get email service instance"""
    return EmailService(settings)


def get_report_service(settings: Annotated[Settings, Depends(get_settings)]) -> ReportService:
    """Get report service instance"""
    return ReportService(settings)