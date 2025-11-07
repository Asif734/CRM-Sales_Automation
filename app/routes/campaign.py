from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.models import CampaignRequest, CampaignResponse, CampaignStats
from app.dependencies import *
from app.services.leads_services import LeadService
from app.services.report_services import ReportService
from app.core.pipeline import CampaignPipeline
import time

router = APIRouter()


@router.post("/run", response_model=CampaignResponse)
async def run_campaign(
    request: CampaignRequest = CampaignRequest(),
    scoring_agent = Depends(get_scoring_agent),
    enrichment_agent = Depends(get_enrichment_agent),
    outreach_agent = Depends(get_outreach_agent),
    email_service = Depends(get_email_service),
    lead_service = Depends(get_lead_service),
    report_service = Depends(get_report_service)
):
    """
    Run a complete campaign:
    1. Read leads from CSV
    2. Score and enrich each lead with AI
    3. Draft personalized emails
    4. Send emails (if enabled)
    5. Save results
    6. Generate report
    """
    start_time = time.time()
    
    try:
        # Read leads
        leads = lead_service.read_leads()
        
        # Run pipeline
        pipeline = CampaignPipeline(
            scoring_agent,
            enrichment_agent,
            outreach_agent,
            email_service
        )
        
        processed_leads = await pipeline.run(leads, request.send_emails)
        
        # Save results
        lead_service.write_leads(processed_leads)
        
        # Generate report
        report_path = await report_service.generate_report(processed_leads)
        
        # Calculate stats
        emails_sent = sum(1 for l in processed_leads if l.email_status == "sent")
        execution_time = time.time() - start_time
        
        return CampaignResponse(
            status="success",
            message=f"Campaign completed successfully! {emails_sent}/{len(processed_leads)} emails sent.",
            leads_processed=len(processed_leads),
            emails_sent=emails_sent,
            report_path=report_path,
            execution_time=round(execution_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign failed: {str(e)}")


@router.get("/stats", response_model=CampaignStats)
async def get_campaign_stats(
    report_service: ReportService = Depends(get_report_service),
    lead_service: LeadService = Depends(get_lead_service)
):
    """Get statistics from the last campaign"""
    try:
        leads = lead_service.read_leads(lead_service.settings.leads_output_path)
        stats = report_service.generate_stats(leads)
        return stats
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No campaign data found. Run a campaign first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))