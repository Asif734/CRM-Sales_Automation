import asyncio
from typing import List
from app.models import Lead
from app.agents.scoring_agent import ScoringAgent
from app.agents.enrichment_agent import EnrichmentAgent
from app.agents.outreach_agents import OutreachAgent
from app.services.email_services import EmailService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CampaignPipeline:
    """Main campaign processing pipeline"""
    
    def __init__(
        self,
        scoring_agent: ScoringAgent,
        enrichment_agent: EnrichmentAgent,
        outreach_agent: OutreachAgent,
        email_service: EmailService
    ):
        self.scoring_agent = scoring_agent
        self.enrichment_agent = enrichment_agent
        self.outreach_agent = outreach_agent
        self.email_service = email_service
    
    async def process_lead(self, lead: Lead, index: int, total: int, send_emails: bool = True) -> Lead:
        """Process a single lead through the entire pipeline"""
        
        logger.info(f"\n{'='*70}")
        logger.info(f"[{index}/{total}] Processing: {lead.name} ({lead.email})")
        logger.info(f"{'='*70}")
        
        try:
            # Step 1: Score the lead
            logger.info(f"📊 Scoring lead...")
            scoring_result = await self.scoring_agent.execute(lead)
            lead.priority = scoring_result.priority
            lead.priority_score = scoring_result.score
            logger.info(f"✓ Priority: {lead.priority} (Score: {lead.priority_score}/10)")
            logger.info(f"  Reasoning: {scoring_result.reasoning}")
            
            # Step 2: Enrich with persona
            logger.info(f"🔍 Enriching lead data...")
            enrichment_result = await self.enrichment_agent.execute(lead)
            lead.ai_persona = enrichment_result.persona
            lead.enrichment_notes = f"{enrichment_result.notes} | Approach: {enrichment_result.suggested_approach}"
            logger.info(f"✓ Persona: {lead.ai_persona}")
            
            # Step 3: Draft outreach email
            logger.info(f"✉️  Drafting personalized email...")
            email_draft = await self.outreach_agent.execute(lead)
            lead.email_subject = email_draft.subject
            lead.email_body = email_draft.body
            logger.info(f"✓ Subject: {lead.email_subject}")
            
            # Step 4: Send email
            if send_emails:
                logger.info(f"📤 Sending email...")
                success = await self.email_service.send_email(lead)
                if not success:
                    logger.warning(f"⚠️  Email failed to send")
            else:
                logger.info(f"⏭️  Skipping email send (dry run)")
                lead.email_status = "draft"
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
            
            return lead
            
        except Exception as e:
            logger.error(f"❌ Error processing lead {lead.email}: {e}")
            lead.email_status = "error"
            return lead
    
    async def run(self, leads: List[Lead], send_emails: bool = True) -> List[Lead]:
        """Run the campaign pipeline for all leads"""
        
        total = len(leads)
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 STARTING CAMPAIGN PIPELINE")
        logger.info(f"{'='*70}")
        logger.info(f"Total leads to process: {total}")
        logger.info(f"Send emails: {send_emails}")
        logger.info(f"{'='*70}\n")
        
        processed_leads = []
        
        for i, lead in enumerate(leads, 1):
            processed_lead = await self.process_lead(lead, i, total, send_emails)
            processed_leads.append(processed_lead)
        
        # Summary
        sent_count = sum(1 for l in processed_leads if l.email_status == "sent")
        high_priority = sum(1 for l in processed_leads if l.priority == "High")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ PIPELINE COMPLETED!")
        logger.info(f"{'='*70}")
        logger.info(f"📊 Summary:")
        logger.info(f"   • Leads processed: {total}")
        logger.info(f"   • Emails sent: {sent_count}")
        logger.info(f"   • High priority: {high_priority}")
        logger.info(f"{'='*70}\n")
        
        return processed_leads