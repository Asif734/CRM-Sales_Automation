from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models import Lead
from app.services.leads_services import LeadService
from app.dependencies import get_lead_service

router = APIRouter()


@router.get("/", response_model=List[Lead])
async def get_leads(service: LeadService = Depends(get_lead_service)):
    """Get all original leads from CSV"""
    try:
        leads = service.read_leads()
        return leads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processed", response_model=List[Lead])
async def get_processed_leads(service: LeadService = Depends(get_lead_service)):
    """Get processed leads with AI enrichment"""
    try:
        leads = service.read_leads(service.settings.leads_output_path)
        return leads
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No processed leads found. Run a campaign first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def get_lead_count(service: LeadService = Depends(get_lead_service)):
    """Get count of leads"""
    try:
        leads = service.read_leads()
        return {
            "total_leads": len(leads)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))