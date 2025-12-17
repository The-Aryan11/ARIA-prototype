"""
ARIA LLM Service - Using Groq (100% FREE)
Llama 3.1 70B - Comparable to GPT-4
"""

from groq import Groq
from typing import List, Dict, Optional, AsyncGenerator
import structlog
import asyncio

from ..core.config import settings

logger = structlog.get_logger()


class LLMService:
    """
    FREE LLM using Groq's Llama 3.1 70B
    """
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        logger.info("LLM Service initialized", model=self.model)
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate response using Groq"""
        
        try:
            # Build messages list
            groq_messages = []
            
            if system_prompt:
                groq_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            for msg in messages:
                groq_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Run sync Groq call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=groq_messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            )
            
            result = response.choices[0].message.content
            logger.info("LLM response generated", tokens=len(result.split()))
            return result
            
        except Exception as e:
            logger.error("LLM generation error", error=str(e))
            return "I apologize, but I'm having a moment. Could you please try again?"
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response using Groq"""
        
        groq_messages = []
        
        if system_prompt:
            groq_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        for msg in messages:
            groq_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=groq_messages,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service