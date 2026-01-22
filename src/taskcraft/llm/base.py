from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger()

class LLMClient(ABC):
    """
    Abstract interface for any LLM provider (Gemini, OpenAI, Anthropic, etc.).
    """
    
    @abstractmethod
    async def generate_response(self, history: List[Dict[str, str]]) -> Any:
        """
        Generates a response based on the conversation history.
        Should return an object that exposes .text and optionally .parts for tool calls.
        """
        pass
