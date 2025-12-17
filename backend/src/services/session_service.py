"""
ARIA Session Service - Cross-Channel Memory
Maintains conversation context across WhatsApp, Web, Store
"""

import json
from datetime import datetime
from typing import Dict, Optional, List
import structlog

from ..core.database import RedisClient, MongoDB

logger = structlog.get_logger()


class SessionService:
    """
    Session management for cross-channel continuity
    """
    
    SESSION_EXPIRY = 60 * 60 * 24 * 30  # 30 days
    
    async def get_session(self, user_id: str) -> Optional[Dict]:
        """Get user session from Redis"""
        try:
            redis = RedisClient.get_client()
            session_data = await redis.get(f"session:{user_id}")
            
            if session_data:
                return json.loads(session_data)
            return None
            
        except Exception as e:
            logger.error("Failed to get session", user_id=user_id, error=str(e))
            return None
    
    async def save_session(self, user_id: str, session: Dict) -> bool:
        """Save session to Redis"""
        try:
            redis = RedisClient.get_client()
            session["last_updated"] = datetime.utcnow().isoformat()
            
            await redis.setex(
                f"session:{user_id}",
                self.SESSION_EXPIRY,
                json.dumps(session, default=str)
            )
            return True
            
        except Exception as e:
            logger.error("Failed to save session", user_id=user_id, error=str(e))
            return False
    
    async def get_or_create_session(self, user_id: str, channel: str) -> Dict:
        """Get existing session or create new one"""
        session = await self.get_session(user_id)
        
        if session is None:
            session = self._create_new_session(user_id, channel)
            await self.save_session(user_id, session)
            logger.info("New session created", user_id=user_id, channel=channel)
        else:
            # Track channel switch
            if session.get("last_channel") != channel:
                session["channel_switches"] = session.get("channel_switches", 0) + 1
                if channel not in session.get("channels_used", []):
                    session["channels_used"].append(channel)
                logger.info("Channel switch detected", 
                          user_id=user_id,
                          from_channel=session.get("last_channel"),
                          to_channel=channel)
            
            session["last_channel"] = channel
            session["last_active"] = datetime.utcnow().isoformat()
        
        return session
    
    def _create_new_session(self, user_id: str, channel: str) -> Dict:
        """Create new session"""
        return {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
            "conversation_history": [],
            "cart": [],
            "preferences": {},
            "style_dna": None,
            "last_channel": channel,
            "channels_used": [channel],
            "channel_switches": 0,
            "name": None,
            "phone": user_id if user_id.startswith("+") else None
        }
    
    async def add_message(
        self, 
        user_id: str, 
        role: str, 
        content: str, 
        channel: str
    ) -> None:
        """Add message to conversation history"""
        session = await self.get_or_create_session(user_id, channel)
        
        message = {
            "role": role,
            "content": content,
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        session["conversation_history"].append(message)
        
        # Keep last 50 messages
        if len(session["conversation_history"]) > 50:
            session["conversation_history"] = session["conversation_history"][-50:]
        
        await self.save_session(user_id, session)
        
        # Also save to MongoDB for analytics
        try:
            conversations = MongoDB.get_collection("conversations")
            await conversations.insert_one({
                "user_id": user_id,
                "role": role,
                "content": content,
                "channel": channel,
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            logger.warning("Failed to save to MongoDB", error=str(e))
    
    async def get_conversation_history(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """Get recent conversation history"""
        session = await self.get_session(user_id)
        if session:
            return session.get("conversation_history", [])[-limit:]
        return []
    
    async def update_style_dna(self, user_id: str, style_dna: Dict) -> None:
        """Update user's style DNA"""
        session = await self.get_session(user_id)
        if session:
            session["style_dna"] = style_dna
            await self.save_session(user_id, session)
            logger.info("Style DNA updated", user_id=user_id)
    
    async def add_to_cart(self, user_id: str, product: Dict) -> None:
        """Add product to cart"""
        session = await self.get_session(user_id)
        if session:
            session["cart"].append({
                **product,
                "added_at": datetime.utcnow().isoformat()
            })
            await self.save_session(user_id, session)
    
    async def get_cart(self, user_id: str) -> List[Dict]:
        """Get user's cart"""
        session = await self.get_session(user_id)
        return session.get("cart", []) if session else []
    
    async def clear_cart(self, user_id: str) -> None:
        """Clear user's cart"""
        session = await self.get_session(user_id)
        if session:
            session["cart"] = []
            await self.save_session(user_id, session)


# Singleton
_session_service = None


def get_session_service() -> SessionService:
    """Get session service singleton"""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service