from app.models import Lead, EnrichmentResult
from app.agents.base import BaseAgent


class EnrichmentAgent(BaseAgent):
    """Agent responsible for enriching lead data with AI insights"""
    
    async def execute(self, lead: Lead) -> EnrichmentResult:
        """Enrich lead with persona and strategic notes"""
        
        system_prompt = """You are a B2B sales strategist specializing in buyer persona development.
Create detailed buyer personas and strategic sales approaches.

Return ONLY valid JSON with this exact structure:
{
  "persona": "Brief persona title",
  "notes": "Key characteristics and motivations",
  "suggested_approach": "Recommended sales strategy"
}"""

        prompt = f"""Create a buyer persona profile for this lead:

Lead Profile:
- Name: {lead.name}
- Role: {lead.role}
- Company: {lead.company} ({lead.company_size} employees)
- Industry: {lead.industry}

Provide:
1. **Persona**: A descriptive title (e.g., "Technical Decision Maker", "Budget Holder", "Innovation Champion")
2. **Notes**: Key characteristics, pain points, and what motivates them
3. **Suggested Approach**: How should we approach this lead? What messaging resonates?

Return JSON format."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            result_dict = await self.llm.parse_json_response(response)
            
            return EnrichmentResult(
                persona=result_dict["persona"],
                notes=result_dict["notes"],
                suggested_approach=result_dict["suggested_approach"]
            )
            
        except Exception as e:
            self.logger.error(f"Error enriching lead {lead.email}: {e}")
            return EnrichmentResult(
                persona="General Business Contact",
                notes="Standard lead profile",
                suggested_approach="Standard outreach approach"
            )