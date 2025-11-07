from app.models import Lead, ScoringResult
from app.agents.base import BaseAgent


class ScoringAgent(BaseAgent):
    """Agent responsible for scoring and prioritizing leads"""
    
    async def execute(self, lead: Lead) -> ScoringResult:
        """Score a lead based on their profile"""
        
        system_prompt = """You are an expert sales lead qualification analyst.
Analyze leads and provide priority scores based on:
- Decision-making authority (role)
- Company size and buying power
- Industry relevance
- Likelihood to convert

Return ONLY valid JSON with this exact structure:
{
  "priority": "High|Medium|Low",
  "score": 1-10,
  "reasoning": "Brief explanation"
}"""

        prompt = f"""Analyze this lead and provide a priority assessment:

Lead Information:
- Name: {lead.name}
- Role: {lead.role}
- Company: {lead.company}
- Industry: {lead.industry}
- Company Size: {lead.company_size}

Consider:
1. Does their role suggest decision-making authority?
2. Is the company size appropriate for our solution?
3. Is the industry a good fit?
4. Overall conversion likelihood?

Return JSON with priority (High/Medium/Low), score (1-10), and reasoning."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            result_dict = await self.llm.parse_json_response(response)
            
            return ScoringResult(
                priority=result_dict["priority"],
                score=result_dict["score"],
                reasoning=result_dict["reasoning"]
            )
            
        except Exception as e:
            self.logger.error(f"Error scoring lead {lead.email}: {e}")
            # Return default score on error
            return ScoringResult(
                priority="Medium",
                score=5,
                reasoning="Error during scoring - assigned default priority"
            )