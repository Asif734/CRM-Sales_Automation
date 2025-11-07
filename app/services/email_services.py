import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models import Lead
from app.config import Settings
from app.utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)


class EmailService:
    """Handle email sending via SMTP"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def send_email(self, lead: Lead) -> bool:
        """Send email to a lead"""
        
        if not lead.email_subject or not lead.email_body:
            logger.error(f"Cannot send email to {lead.email}: missing subject or body")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
            message['To'] = lead.email
            message['Subject'] = lead.email_subject
            
            # Add body
            message.attach(MIMEText(lead.email_body, 'plain'))
            
            # Send via SMTP
            await aiosmtplib.send(
                message,
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
            )
            
            # Update lead
            lead.email_sent_at = datetime.now()
            lead.email_status = "sent"
            
            logger.info(f"✓ Email sent successfully to {lead.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {lead.email}: {e}")
            lead.email_status = f"failed"
            return False