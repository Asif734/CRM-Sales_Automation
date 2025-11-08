"""
Response handling module - categorizes and manages email responses
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from app.models import Lead
from app.utils.llm_client import LLMClient
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ResponseCategory(str, Enum):
    """Email response categories"""
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    REQUEST_MORE_INFO = "request_more_info"
    OUT_OF_OFFICE = "out_of_office"
    MEETING_SCHEDULED = "meeting_scheduled"
    UNSUBSCRIBE = "unsubscribe"
    BOUNCE = "bounce"
    SPAM_COMPLAINT = "spam_complaint"
    UNKNOWN = "unknown"


class EmailResponse(BaseModel):
    """Email response data model"""
    lead_email: str
    response_body: str
    received_at: datetime
    category: ResponseCategory
    sentiment: Optional[str] = None  # positive, neutral, negative
    action_required: bool = False
    priority: Optional[str] = None
    ai_summary: Optional[str] = None


class Responder:
    """
    Intelligent email response handler using AI classification
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.responses = []
    
    async def classify_response(
        self, 
        lead: Lead, 
        response_body: str,
        received_at: Optional[datetime] = None
    ) -> EmailResponse:
        """
        Classify an email response using AI
        
        Args:
            lead: Original lead who responded
            response_body: The email response text
            received_at: When response was received
        
        Returns:
            EmailResponse with classification
        """
        
        if received_at is None:
            received_at = datetime.now()
        
        logger.info(f"Classifying response from {lead.email}...")
        
        try:
            # Use AI to classify
            classification = await self._ai_classify(lead, response_body)
            
            # Create response object
            response = EmailResponse(
                lead_email=lead.email,
                response_body=response_body,
                received_at=received_at,
                category=classification["category"],
                sentiment=classification.get("sentiment"),
                action_required=classification.get("action_required", False),
                priority=classification.get("priority"),
                ai_summary=classification.get("summary")
            )
            
            # Update lead
            lead.response_category = response.category
            
            # Track response
            self.responses.append(response)
            
            logger.info(f"✓ Response classified: {response.category} (Sentiment: {response.sentiment})")
            
            return response
            
        except Exception as e:
            logger.error(f"Error classifying response from {lead.email}: {e}")
            
            # Return unknown classification
            return EmailResponse(
                lead_email=lead.email,
                response_body=response_body,
                received_at=received_at,
                category=ResponseCategory.UNKNOWN,
                sentiment="neutral",
                action_required=False,
                ai_summary="Error during classification"
            )
    
    async def _ai_classify(self, lead: Lead, response_body: str) -> Dict[str, Any]:
        """Use AI to classify email response"""
        
        system_prompt = """You are an expert email response analyzer for sales campaigns.
Classify email responses into categories and analyze sentiment.

Return ONLY valid JSON with this structure:
{
  "category": "interested|not_interested|request_more_info|out_of_office|meeting_scheduled|unsubscribe|bounce|spam_complaint|unknown",
  "sentiment": "positive|neutral|negative",
  "action_required": true/false,
  "priority": "high|medium|low",
  "summary": "Brief summary of the response"
}"""

        prompt = f"""Classify this email response:

Original Lead:
- Name: {lead.name}
- Company: {lead.company}
- Our Subject: {lead.email_subject or 'N/A'}

Their Response:
{response_body}

Analyze:
1. **Category**: What type of response is this?
   - interested: Shows interest in learning more
   - not_interested: Polite decline or not interested
   - request_more_info: Asking for more details
   - out_of_office: Auto-reply, out of office
   - meeting_scheduled: Ready to schedule a call/meeting
   - unsubscribe: Wants to unsubscribe
   - bounce: Email bounced back
   - spam_complaint: Marked as spam
   - unknown: Can't determine

2. **Sentiment**: positive, neutral, or negative

3. **Action Required**: Does this need immediate follow-up?

4. **Priority**: How urgent is this response?

5. **Summary**: Brief summary for sales team

Return JSON format."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            result = await self.llm.parse_json_response(response)
            return result
            
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            # Return safe default
            return {
                "category": "unknown",
                "sentiment": "neutral",
                "action_required": False,
                "priority": "low",
                "summary": "Unable to classify"
            }
    
    async def batch_classify(self, responses: List[Dict]) -> List[EmailResponse]:
        """
        Classify multiple responses
        
        Args:
            responses: List of dicts with 'lead' and 'response_body' keys
        
        Returns:
            List of classified EmailResponse objects
        """
        results = []
        
        for item in responses:
            lead = item['lead']
            body = item['response_body']
            received = item.get('received_at')
            
            classified = await self.classify_response(lead, body, received)
            results.append(classified)
        
        return results
    
    def get_responses_by_category(self, category: ResponseCategory) -> List[EmailResponse]:
        """Get all responses in a specific category"""
        return [r for r in self.responses if r.category == category]
    
    def get_action_required(self) -> List[EmailResponse]:
        """Get all responses requiring action"""
        return [r for r in self.responses if r.action_required]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get response statistics"""
        if not self.responses:
            return {
                "total_responses": 0,
                "by_category": {},
                "by_sentiment": {},
                "action_required_count": 0
            }
        
        # Count by category
        by_category = {}
        for response in self.responses:
            cat = response.category
            by_category[cat] = by_category.get(cat, 0) + 1
        
        # Count by sentiment
        by_sentiment = {}
        for response in self.responses:
            sent = response.sentiment
            if sent:
                by_sentiment[sent] = by_sentiment.get(sent, 0) + 1
        
        # Action required
        action_count = len([r for r in self.responses if r.action_required])
        
        return {
            "total_responses": len(self.responses),
            "by_category": by_category,
            "by_sentiment": by_sentiment,
            "action_required_count": action_count,
            "interested_count": len(self.get_responses_by_category(ResponseCategory.INTERESTED)),
            "response_rate": "N/A"  # Would need total sent count
        }
    
    async def generate_follow_up(self, response: EmailResponse, lead: Lead) -> str:
        """
        Generate AI follow-up email based on response
        
        Args:
            response: The classified response
            lead: Original lead
        
        Returns:
            Suggested follow-up email text
        """
        
        if response.category in [ResponseCategory.NOT_INTERESTED, ResponseCategory.UNSUBSCRIBE]:
            return "No follow-up recommended. Lead has declined."
        
        system_prompt = """You are an expert sales follow-up writer.
Generate appropriate follow-up emails based on the prospect's response.
Keep it brief, professional, and action-oriented."""

        prompt = f"""Generate a follow-up email:

Lead: {lead.name} at {lead.company}
Their Response Category: {response.category}
Their Response: {response.response_body}
Sentiment: {response.sentiment}

AI Summary: {response.ai_summary}

Write a brief follow-up email (under 100 words) that:
1. Acknowledges their response
2. Provides relevant next steps
3. Makes it easy for them to respond
4. Matches the tone of their reply

Return only the email body, no subject."""

        try:
            follow_up = await self.llm.generate(prompt, system_prompt)
            return follow_up.strip()
        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")
            return f"Thank you for your response. I'd love to continue our conversation. When would be a good time to connect?"
    
    def reset_stats(self):
        """Reset response tracking"""
        self.responses = []


# Example usage in comments:
"""
# Initialize responder
responder = Responder(llm_client)

# Classify a response
response = await responder.classify_response(
    lead=some_lead,
    response_body="Thanks for reaching out! I'd love to learn more about your solution."
)

# Get all interested leads
interested = responder.get_responses_by_category(ResponseCategory.INTERESTED)

# Get responses needing action
action_needed = responder.get_action_required()

# Generate follow-up
follow_up = await responder.generate_follow_up(response, lead)

# Get stats
stats = responder.get_stats()
"""