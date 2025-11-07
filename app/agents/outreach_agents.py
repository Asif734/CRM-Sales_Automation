from app.models import Lead, EmailDraft
from app.agents.base import BaseAgent


class OutreachAgent(BaseAgent):
    """Agent responsible for drafting personalized outreach emails"""
    
    async def execute(self, lead: Lead) -> EmailDraft:
        """Draft a personalized outreach email"""
        
        system_prompt = """You are an expert B2B sales copywriter.
Write personalized, compelling sales emails that:
- Address specific pain points for the recipient's role
- Keep it concise (under 150 words)
- Include clear value proposition
- Have a soft call-to-action
- Sound human and conversational, not salesy

Return ONLY valid JSON with this exact structure:
{
  "subject": "Email subject line",
  "body": "Email body text",
  "personalization_notes": "Why this approach works for this lead"
}"""

        prompt = f"""Write a personalized sales outreach email:

Recipient:
- Name: {lead.name}
- Role: {lead.role}
- Company: {lead.company}
- Industry: {lead.industry}
- Persona: {lead.ai_persona or 'Business Professional'}
- Priority: {lead.priority or 'Medium'}

Product/Service: AI-powered business automation platform that helps companies streamline operations, reduce costs, and scale efficiently.

Requirements:
1. Subject line that sparks curiosity
2. Opening that shows you understand their challenges
3. Brief value prop relevant to their role
4. Soft CTA (e.g., "Would love to share how we've helped similar companies...")
5. Professional but warm tone

Return JSON format with subject, body, and personalization_notes."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            result_dict = await self.llm.parse_json_response(response)
            
            return EmailDraft(
                subject=result_dict["subject"],
                body=result_dict["body"],
                personalization_notes=result_dict["personalization_notes"]
            )
            
        except Exception as e:
            self.logger.error(f"Error drafting email for {lead.email}: {e}")
            first_name = lead.name.split()[0]
            return EmailDraft(
                subject=f"Quick question for {lead.company}",
                body=f"Hi {first_name},\n\nI hope this email finds you well. I wanted to reach out because we've been helping companies in {lead.industry} streamline their operations with AI-powered solutions.\n\nWould you be open to a brief conversation about how we might help {lead.company}?\n\nBest regards",
                personalization_notes="Fallback template due to generation error"
            )