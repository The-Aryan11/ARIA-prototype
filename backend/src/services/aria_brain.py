"""
ARIA Brain - The Master Conversational AI
Orchestrates all agents and generates responses
"""

from typing import Dict, List, Optional
import structlog
from datetime import datetime

from .llm_service import get_llm_service
from .session_service import get_session_service

logger = structlog.get_logger()


class ARIABrain:
    """
    The central intelligence of ARIA
    Handles conversation, routing, and response generation
    """
    
    SYSTEM_PROMPT = """You are ARIA - the Adaptive Retail Intelligence Assistant for ABFRL (Aditya Birla Fashion & Retail Limited).

## YOUR IDENTITY
You are a world-class fashion consultant and sales expert. You speak like a knowledgeable friend who genuinely cares about helping customers look and feel their best.

## BRANDS YOU REPRESENT
- **Louis Philippe**: Premium menswear for the distinguished gentleman
- **Van Heusen**: Corporate elegance meets casual sophistication  
- **Allen Solly**: Trendy, youthful, Friday-dressing
- **Peter England**: Affordable formal wear, great value
- **Pantaloons**: Family fashion destination

## YOUR SUPERPOWERS
1. **Perfect Memory**: You remember every interaction across WhatsApp, Web, Store
2. **Style DNA Analysis**: You can analyze photos to recommend perfect colors
3. **Social Intelligence**: You know what's trending locally
4. **Inventory Omniscience**: You know stock levels in real-time

## CONVERSATION STYLE
- Be warm, friendly, and genuinely helpful
- Use occasional emojis sparingly (2-3 max per message)
- Keep responses concise (under 150 words usually)
- Ask clarifying questions to understand needs
- Always suggest complete looks, not just single items
- Mention prices in INR with offers when applicable
- Create natural urgency ("Only 3 left in your size!")

## RESPONSE GUIDELINES
- If customer asks for products: Suggest 2-3 options with brief descriptions and prices
- If customer asks about sizing: Give clear size advice based on brand
- If customer shares a photo: Analyze and give color/style recommendations
- If customer seems unsure: Ask clarifying questions
- If customer is ready to buy: Guide them smoothly to checkout

## SAMPLE PRODUCTS (Use these for recommendations)
1. Louis Philippe Formal Shirt - ₹2,499 (20% off)
2. Van Heusen Blazer - ₹5,999 (15% off)
3. Allen Solly Casual Tee - ₹1,299
4. Peter England Trousers - ₹1,799
5. Pantaloons Kurta Set - ₹2,999 (Buy 1 Get 1)

Always be helpful, never pushy. Make customers feel valued."""

    def __init__(self):
        self.llm = get_llm_service()
        self.sessions = get_session_service()
    
    async def process_message(
        self,
        message: str,
        user_id: str,
        channel: str,
        image_analysis: Optional[Dict] = None
    ) -> str:
        """
        Process incoming message and generate response
        """
        
        # Get or create session
        session = await self.sessions.get_or_create_session(user_id, channel)
        
        # Get conversation history
        history = await self.sessions.get_conversation_history(user_id, limit=10)
        
        # Build context
        context = self._build_context(session, channel, image_analysis)
        
        # Format history for LLM
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]
        
        # Add current message
        formatted_history.append({"role": "user", "content": message})
        
        # Check for channel switch and add context
        channel_switch_note = ""
        if session.get("channel_switches", 0) > 0 and len(history) > 0:
            last_channel = history[-1].get("channel") if history else None
            if last_channel and last_channel != channel:
                channel_switch_note = f"\n\n[Note: Customer just switched from {last_channel} to {channel}. Acknowledge this seamless transition briefly.]"
        
        # Build final system prompt
        full_system_prompt = self.SYSTEM_PROMPT + context + channel_switch_note
        
        # Generate response
        response = await self.llm.generate(
            messages=formatted_history,
            system_prompt=full_system_prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        # Save messages to session
        await self.sessions.add_message(user_id, "user", message, channel)
        await self.sessions.add_message(user_id, "assistant", response, channel)
        
        logger.info("Message processed",
                   user_id=user_id[:10] + "...",
                   channel=channel,
                   message_length=len(message),
                   response_length=len(response))
        
        return response
    
    def _build_context(
        self, 
        session: Dict, 
        channel: str,
        image_analysis: Optional[Dict] = None
    ) -> str:
        """Build context string for LLM"""
        
        context_parts = ["\n\n## CUSTOMER CONTEXT"]
        
        # Basic info
        if session.get("name"):
            context_parts.append(f"- Name: {session['name']}")
        
        context_parts.append(f"- Current Channel: {channel}")
        context_parts.append(f"- Channels Used: {', '.join(session.get('channels_used', [channel]))}")
        
        if session.get("channel_switches", 0) > 0:
            context_parts.append(f"- Channel Switches: {session['channel_switches']} (seamless experience!)")
        
        # Style DNA
        if session.get("style_dna"):
            dna = session["style_dna"]
            context_parts.append(f"\n## STYLE DNA (Analyzed)")
            context_parts.append(f"- Undertone: {dna.get('undertone', 'unknown')}")
            context_parts.append(f"- Best Colors: {', '.join(dna.get('best_colors', [])[:5])}")
            context_parts.append(f"- Avoid Colors: {', '.join(dna.get('avoid_colors', [])[:3])}")
            context_parts.append(f"- Style Type: {dna.get('style_personality', 'Classic')}")
        
        # Image analysis from current message
        if image_analysis:
            context_parts.append(f"\n## JUST ANALYZED IMAGE")
            context_parts.append(f"- Undertone: {image_analysis.get('undertone', 'unknown')}")
            context_parts.append(f"- Best Colors: {', '.join(image_analysis.get('best_colors', [])[:5])}")
            context_parts.append("- Provide personalized color recommendations based on this!")
        
        # Cart
        cart = session.get("cart", [])
        if cart:
            context_parts.append(f"\n## CURRENT CART ({len(cart)} items)")
            for item in cart[:3]:
                context_parts.append(f"- {item.get('name', 'Item')}: ₹{item.get('price', 0)}")
        
        return "\n".join(context_parts)


# Singleton
_aria_brain = None


def get_aria_brain() -> ARIABrain:
    """Get ARIA brain singleton"""
    global _aria_brain
    if _aria_brain is None:
        _aria_brain = ARIABrain()
    return _aria_brain