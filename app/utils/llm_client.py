from groq import Groq
from app.config import Settings
import json
from app.utils.logger import setup_logger
from typing import Optional

logger = setup_logger(__name__)


class LLMClient:
    """Groq LLM client wrapper"""
    
    def __init__(self, settings: Settings):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.temperature = settings.groq_temperature
        self.max_tokens = settings.groq_max_tokens
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """Generate completion from Groq"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    async def parse_json_response(self, response: str) -> dict:
        """Parse JSON response from LLM"""
        try:
            # Clean markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}. Response: {response}")
            raise