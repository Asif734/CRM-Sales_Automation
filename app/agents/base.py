from abc import ABC, abstractmethod
from app.utils.llm_client import LLMClient
from app.utils.logger import setup_logger


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = setup_logger(self.__class__.__name__)
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Execute agent logic"""
        pass