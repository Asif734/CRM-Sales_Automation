"""
Email handling module - manages email composition, sending, and tracking
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime
from app.models import Lead
from app.config import Settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailerException(Exception):
    """Custom exception for emailer errors"""
    pass


class Emailer:
    """
    Advanced email handler with templates, tracking, and batch sending
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sent_count = 0
        self.failed_count = 0
        self.email_history = []
    
    async def send_email(
        self, 
        lead: Lead,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        cc: Optional[list] = None,
        bcc: Optional[list] = None,
        attachments: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send email to a lead with tracking
        
        Args:
            lead: Lead object with email details
            subject: Override email subject
            body: Override email body
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachments (not implemented in MVP)
        
        Returns:
            Dict with status and metadata
        """
        
        # Use lead's drafted email if no override
        email_subject = subject or lead.email_subject
        email_body = body or lead.email_body
        
        if not email_subject or not email_body:
            error_msg = f"Missing subject or body for {lead.email}"
            logger.error(error_msg)
            raise EmailerException(error_msg)
        
        try:
            # Create message
            message = self._create_message(
                to_email=lead.email,
                to_name=lead.name,
                subject=email_subject,
                body=email_body,
                cc=cc,
                bcc=bcc
            )
            
            # Send via SMTP
            send_result = await self._send_smtp(message, lead.email)
            
            # Update lead tracking
            lead.email_sent_at = datetime.now()
            lead.email_status = "sent"
            
            # Track internally
            self.sent_count += 1
            self._track_email(lead, "sent", send_result)
            
            logger.info(f"✓ Email sent to {lead.email} - Subject: {email_subject}")
            
            return {
                "status": "sent",
                "email": lead.email,
                "subject": email_subject,
                "sent_at": lead.email_sent_at,
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {lead.email}: {e}")
            
            # Update lead
            lead.email_status = "failed"
            lead.email_sent_at = datetime.now()
            
            # Track failure
            self.failed_count += 1
            self._track_email(lead, "failed", {"error": str(e)})
            
            return {
                "status": "failed",
                "email": lead.email,
                "subject": email_subject,
                "error": str(e),
                "message": f"Failed to send: {str(e)}"
            }
    
    def _create_message(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body: str,
        cc: Optional[list] = None,
        bcc: Optional[list] = None
    ) -> MIMEMultipart:
        """Create MIME message"""
        
        message = MIMEMultipart()
        message['From'] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
        message['To'] = f"{to_name} <{to_email}>"
        message['Subject'] = subject
        
        if cc:
            message['Cc'] = ', '.join(cc)
        if bcc:
            message['Bcc'] = ', '.join(bcc)
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        return message
    
    async def _send_smtp(self, message: MIMEMultipart, recipient: str) -> Dict[str, Any]:
        """Send message via SMTP"""
        
        try:
            await aiosmtplib.send(
                message,
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                timeout=30
            )
            
            return {
                "smtp_host": self.settings.smtp_host,
                "smtp_port": self.settings.smtp_port,
                "timestamp": datetime.now().isoformat()
            }
            
        except aiosmtplib.SMTPException as e:
            raise EmailerException(f"SMTP error: {str(e)}")
        except Exception as e:
            raise EmailerException(f"Network error: {str(e)}")
    
    def _track_email(self, lead: Lead, status: str, metadata: Dict):
        """Track email for analytics"""
        self.email_history.append({
            "email": lead.email,
            "name": lead.name,
            "company": lead.company,
            "status": status,
            "subject": lead.email_subject,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        })
    
    async def send_batch(self, leads: list[Lead], delay: float = 0.5) -> Dict[str, Any]:
        """
        Send emails to multiple leads with delay between sends
        
        Args:
            leads: List of leads to email
            delay: Seconds to wait between sends (rate limiting)
        
        Returns:
            Batch send summary
        """
        import asyncio
        
        results = []
        
        for i, lead in enumerate(leads, 1):
            logger.info(f"[{i}/{len(leads)}] Sending to {lead.email}...")
            
            result = await self.send_email(lead)
            results.append(result)
            
            # Rate limiting delay
            if i < len(leads):
                await asyncio.sleep(delay)
        
        return {
            "total": len(leads),
            "sent": self.sent_count,
            "failed": self.failed_count,
            "results": results
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get email sending statistics"""
        return {
            "total_sent": self.sent_count,
            "total_failed": self.failed_count,
            "success_rate": (self.sent_count / (self.sent_count + self.failed_count) * 100) 
                           if (self.sent_count + self.failed_count) > 0 else 0,
            "history_count": len(self.email_history)
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.sent_count = 0
        self.failed_count = 0
        self.email_history = []


# Singleton instance helper
_emailer_instance = None


def get_emailer(settings: Settings) -> Emailer:
    """Get or create emailer instance"""
    global _emailer_instance
    if _emailer_instance is None:
        _emailer_instance = Emailer(settings)
    return _emailer_instance