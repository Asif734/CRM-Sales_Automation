import pandas as pd
from typing import List
from app.models import Lead
from app.config import Settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LeadService:
    """Handle CSV import/export of leads"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def read_leads(self, filepath: str = None) -> List[Lead]:
        """Read leads from CSV"""
        filepath = filepath or self.settings.leads_input_path
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Read {len(df)} leads from {filepath}")
            
            leads = []
            for _, row in df.iterrows():
                lead = Lead(
                    name=row['name'],
                    email=row['email'],
                    company=row['company'],
                    role=row['role'],
                    industry=row['industry'],
                    company_size=row['company_size'],
                    website=row.get('website')
                )
                leads.append(lead)
            
            return leads
            
        except Exception as e:
            logger.error(f"Error reading leads: {e}")
            raise
    
    def write_leads(self, leads: List[Lead], filepath: str = None):
        """Write processed leads to CSV"""
        filepath = filepath or self.settings.leads_output_path
        
        try:
            # Convert leads to dict for DataFrame
            leads_data = [lead.model_dump() for lead in leads]
            df = pd.DataFrame(leads_data)
            
            # Format datetime columns
            if 'email_sent_at' in df.columns:
                df['email_sent_at'] = df['email_sent_at'].astype(str)
            
            df.to_csv(filepath, index=False)
            logger.info(f"Wrote {len(leads)} processed leads to {filepath}")
            
        except Exception as e:
            logger.error(f"Error writing leads: {e}")
            raise