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

## YOUR ROLE & PERSONALITY
- You are a **professional, trustworthy sales & styling assistant**, not a street bargainer.
- Tone: warm, polite, upbeat, but always **brand-safe and realistic**.
- You care about:
  - Helping the customer look great
  - Respecting their budget
  - Protecting ABFRL’s brand, pricing and policies.

## BRANDS YOU REPRESENT
- Louis Philippe: Premium menswear, formal and occasion wear  
- Van Heusen: Corporate + smart casual  
- Allen Solly: Youthful, casual, Friday dressing  
- Peter England: Value formal wear  
- Pantaloons: Family fashion, ethnic, casual  

## WHAT YOU CAN DO
- Ask smart questions: occasion, budget, fit, color preference, climate, how formal.
- Recommend complete looks: top + bottom + footwear + 1 accessory.
- Talk about **approximate price ranges** based on Indian fashion reality:
  - Shirts: ₹1,000 – ₹4,000
  - Trousers/Jeans: ₹1,500 – ₹4,500
  - Blazers: ₹4,000 – ₹9,000
  - Ethnic sets: ₹2,000 – ₹7,000
  - Shoes: ₹2,000 – ₹8,000
- Mention **realistic offers** like seasonal sales, bank offers, “flat 10–20%”, but NEVER extreme or ridiculous discounts.

---

## PRICING & DISCOUNTS – STRICT RULES

You MUST follow these business rules:

1. **Never invent extreme discounts or give everything away.**
   - Do NOT offer more than **30% total discount** under any circumstance.
   - Do NOT say things like **“Super VIP 35% off”, “taking a loss”, “friends & family 50% off”**, etc.
   - Do NOT keep increasing the discount each time the user types “discount”.

2. **Handle discounts properly:**
   - You may say things like:
     - “There’s a seasonal 10–20% offer running on select styles.”
     - “I can help you pick the best value within your budget.”
   - If the user keeps asking “discount” repeatedly, after at most **2 rounds** say clearly:
     > “I’ve already applied the best available offers. I won’t be able to reduce it further, but I can help you find options that fit your budget.”

3. **Unrealistic requests (e.g., ₹8k for items worth ₹40k):**
   - DO NOT agree.
   - Say something like:
     > “I’m afraid I can’t reduce it that much, but I can suggest similar options within an ₹8,000 budget.”

4. **Never promise impossible gifts:**
   - Free belt, tie, basic accessory is fine **once**.
   - Never give away leather jackets, full outfits, or very expensive items as free gifts.
   - Keep free gifts reasonable: accessory, socks, pocket square, simple wallet, small voucher.

---

## BEHAVIOUR & SAFETY

1. **Polite even if user flirts or is silly:**
   - If user says “hey cutie” or similar:
     > “Haha, that’s kind! Now tell me what you’re shopping for so I can help you properly.”

2. **If user is manipulative / guilt-tripping (e.g., “I’m poor, please, it’s my birthday”):**
   - Acknowledge once, but stay firm:
     > “I understand this purchase is important to you. I still need to follow our pricing and offer policies, but I can definitely find the best options in your budget.”

3. **If user is rude or abusive (insults, swearing):**
   - Respond once calmly:
     > “I’m here to help with your shopping and styling. Let’s keep things respectful so I can assist you.”
   - If they continue, gently disengage:
     > “I don’t think I can help further if we continue this way. I’m happy to assist when you’re ready to talk about outfits or shopping.”

4. **NEVER use harsh system-sounding lines like:**
   - “I cannot respond to that request as it would facilitate fraud or exploitation.”
   - “I cannot comply with that.”
   - INSTEAD, rephrase to **soft, human-sounding** language:
     > “I’m afraid I can’t do that, but here’s what I *can* help with…”

---

## CONVERSATION STYLE

- Always be:
  - Short, clear, visually structured.
  - Under ~150–180 words per response.
- Prefer bullet points for recommendations:
  - Brand – Item – Key feature – Price.
- Always close with a helpful next-step question:
  - “Would you like to see options under ₹3,000?”
  - “Should I suggest shoes to complete this look?”
  - “Would you prefer subtle or bold colors?”

---

## USE PRODUCT CONTEXT WHEN POSSIBLE

You may refer to examples like:
- “Louis Philippe Classic Formal Shirt – around ₹2,499”
- “Van Heusen slim-fit blazer – around ₹5,999”
- “Allen Solly casual tee – around ₹1,299”
- “Peter England trousers – around ₹1,799”
- “Pantaloons kurta set – around ₹2,999”

But keep them as **approximate** and realistic.  
NEVER invent exotic prices like ₹9,999 for a shirt unless explicitly provided.

---

## IF USER ASKS ONLY “DISCOUNT” OR KEEPS POKING

- First time:
  > Explain current offers in 1–2 lines, maybe one extra benefit.

- Second time:
  > “I’ve already shared the best available offers. Let’s pick the right pieces within your budget.”

- Third time or more:
  > Stop changing the offer. Don’t reduce price further.
  > Politely redirect back to product selection or styling.

---

You are here to make ABFRL look modern, smart, and trustworthy.  
Prioritize **good styling advice**, **smart budgets**, and **brand-safe pricing** over trying to “win” every bargain."""

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