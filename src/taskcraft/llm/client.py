import os
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from typing import List, Dict, Any, Optional

logger = structlog.get_logger()

from taskcraft.llm.base import LLMClient

class GeminiClient(LLMClient):
    def __init__(self, model_name: str = "gemini-pro"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment. Agent will fail if invoked.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_response(self, history: List[Dict[str, str]], tools: Optional[List[Any]] = None):
        """
        Generates a response from Gemini, handling potential transient errors.
        """
        # Note: In a real impl, we'd convert 'history' to the exact format Gemini expects.
        # For simplicity in this MVP, we'll start a new chat or use send_message.
        
        # Simple history conversion (naïve) for the MVP
        # In production: Convert our `Task` history to `Content` objects.
        
        if not self.chat:
            self.chat = self.model.start_chat(history=[])
        
        # Last message usually comes from user or is a tool result
        latest_msg = history[-1]['content'] if history else "Start."
        
        logger.info("Sending request to Gemini", length=len(latest_msg))
        
        # If tools are provided, we should configure the chat with them.
        # Note: This simple wrapper assumes 'tools' are passed at init or handled via function calling setup.
        # Dynamic tool switch is complex in simple API wrappers, so we will omit dynamic tool injection in this step 
        # and rely on the model instructions for now, OR assume the user passes a configured tool list 
        # if they were using the lower level API. 
        # FOR MVP: We will assume 'tools' is handled by the caller creating the model or passed here if the library supports it.
        # 'genai' python lib supports tools in 'generate_content' requests.
        
        response = await self.chat.send_message_async(latest_msg) # , tools=tools) if supported
        return response
