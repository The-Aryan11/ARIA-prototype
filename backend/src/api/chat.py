"""
ARIA Chat API - Web/App Chat Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import structlog

from ..services.aria_brain import get_aria_brain
from ..services.session_service import get_session_service

logger = structlog.get_logger()
router = APIRouter(prefix="/chat", tags=["Chat"])


# ============== Request/Response Models ==============

class ChatRequest(BaseModel):
    """Chat request from web/app"""
    user_id: str
    message: str
    channel: str = "web"


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    user_id: str
    channel: str
    session_info: Optional[Dict] = None


class SessionInfoRequest(BaseModel):
    """Get session info request"""
    user_id: str


class SessionInfoResponse(BaseModel):
    """Session information"""
    user_id: str
    channels_used: List[str]
    channel_switches: int
    cart_items: int
    has_style_dna: bool
    last_channel: Optional[str]


# ============== Endpoints ==============

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message and get AI response
    
    This is the main chat endpoint for web/app channels.
    Demonstrates cross-channel session continuity.
    """
    
    try:
        brain = get_aria_brain()
        sessions = get_session_service()
        
        # Process message through ARIA brain
        response = await brain.process_message(
            message=request.message,
            user_id=request.user_id,
            channel=request.channel
        )
        
        # Get session info for response
        session = await sessions.get_session(request.user_id)
        session_info = None
        
        if session:
            session_info = {
                "channels_used": session.get("channels_used", []),
                "channel_switches": session.get("channel_switches", 0),
                "cart_count": len(session.get("cart", [])),
                "has_style_dna": session.get("style_dna") is not None
            }
        
        logger.info("Chat message processed",
                   user_id=request.user_id[:10] + "...",
                   channel=request.channel)
        
        return ChatResponse(
            response=response,
            user_id=request.user_id,
            channel=request.channel,
            session_info=session_info
        )
        
    except Exception as e:
        logger.error("Chat error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session", response_model=SessionInfoResponse)
async def get_session_info(request: SessionInfoRequest):
    """
    Get session information for a user
    
    Shows cross-channel history and session state.
    """
    
    try:
        sessions = get_session_service()
        session = await sessions.get_session(request.user_id)
        
        if not session:
            return SessionInfoResponse(
                user_id=request.user_id,
                channels_used=[],
                channel_switches=0,
                cart_items=0,
                has_style_dna=False,
                last_channel=None
            )
        
        return SessionInfoResponse(
            user_id=request.user_id,
            channels_used=session.get("channels_used", []),
            channel_switches=session.get("channel_switches", 0),
            cart_items=len(session.get("cart", [])),
            has_style_dna=session.get("style_dna") is not None,
            last_channel=session.get("last_channel")
        )
        
    except Exception as e:
        logger.error("Session info error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20):
    """
    Get conversation history for a user
    
    Returns messages across all channels.
    """
    
    try:
        sessions = get_session_service()
        history = await sessions.get_conversation_history(user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "messages": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error("History error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{user_id}")
async def clear_session(user_id: str):
    """
    Clear session for a user (for testing)
    """
    
    try:
        from ..core.database import RedisClient
        redis = RedisClient.get_client()
        await redis.delete(f"session:{user_id}")
        
        return {"message": "Session cleared", "user_id": user_id}
        
    except Exception as e:
        logger.error("Clear session error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))