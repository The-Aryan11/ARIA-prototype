"""
ARIA WhatsApp Webhook - Twilio Integration
Handles incoming WhatsApp messages
"""

from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import PlainTextResponse
from typing import Optional
import structlog

from ..services.aria_brain import get_aria_brain
from ..services.whatsapp_service import get_whatsapp_service
from ..services.session_service import get_session_service
from ..services.color_analysis import get_color_service
from ..core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification for Twilio
    Twilio will call this to verify the webhook is working
    """
    return PlainTextResponse("ARIA WhatsApp Webhook Active")


@router.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(default=""),
    NumMedia: str = Form(default="0"),
    MediaUrl0: Optional[str] = Form(default=None),
    MediaContentType0: Optional[str] = Form(default=None),
):
    """
    Handle incoming WhatsApp messages from Twilio
    
    This is where the magic happens:
    - Receives message from WhatsApp
    - Processes through ARIA brain
    - Handles images for color analysis
    - Sends response back
    """
    
    try:
        # Extract phone number (remove 'whatsapp:' prefix)
        user_id = From.replace("whatsapp:", "")
        message = Body.strip()
        
        logger.info("WhatsApp message received",
                   from_number=user_id[:10] + "...",
                   has_media=int(NumMedia) > 0)
        
        brain = get_aria_brain()
        whatsapp = get_whatsapp_service()
        sessions = get_session_service()
        
        image_analysis = None
        
        # Handle image message (for color analysis)
        if int(NumMedia) > 0 and MediaUrl0:
            if MediaContentType0 and MediaContentType0.startswith("image"):
                logger.info("Processing image for color analysis")
                
                # Download and analyze image
                media_bytes = await whatsapp.download_media(MediaUrl0)
                
                if media_bytes:
                    color_service = get_color_service()
                    image_analysis = color_service.analyze_from_bytes(media_bytes)
                    
                    # Save Style DNA to session
                    await sessions.update_style_dna(user_id, image_analysis)
                    
                    # Create special response for color analysis
                    response = f"""✨ *Style DNA Analysis Complete!*

🎨 *Your Undertone:* {image_analysis['undertone'].title()}

🌈 *Colors That Suit You:*
{', '.join(image_analysis['best_colors'][:5])}

🚫 *Colors to Avoid:*
{', '.join(image_analysis['avoid_colors'][:3])}

👗 *Style Type:* {image_analysis['style_personality']}
⭐ *Celebrity Match:* {image_analysis['celebrity_match']}

Now I can recommend outfits that will look *amazing* on you! 

What are you shopping for today? 👠👔👗"""
                    
                    # Save messages
                    await sessions.add_message(user_id, "user", "[Sent a photo for analysis]", "whatsapp")
                    await sessions.add_message(user_id, "assistant", response, "whatsapp")
                    
                    return whatsapp.create_response(response)
        
        # Handle text message
        if not message:
            message = "Hi"
        
        # Process through ARIA brain
        response = await brain.process_message(
            message=message,
            user_id=user_id,
            channel="whatsapp",
            image_analysis=image_analysis
        )
        
        logger.info("WhatsApp response generated",
                   to_number=user_id[:10] + "...",
                   response_length=len(response))
        
        # Return TwiML response
        return PlainTextResponse(
            content=whatsapp.create_response(response),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error("WhatsApp webhook error", error=str(e))
        
        # Return friendly error message
        whatsapp = get_whatsapp_service()
        error_response = "Oops! I had a small hiccup. Could you please try again? 🙏"
        
        return PlainTextResponse(
            content=whatsapp.create_response(error_response),
            media_type="application/xml"
        )


@router.post("/send")
async def send_whatsapp_message(
    to_number: str,
    message: str
):
    """
    Send a WhatsApp message (for testing)
    
    Note: Only works with numbers that have joined the sandbox
    """
    
    try:
        whatsapp = get_whatsapp_service()
        success = await whatsapp.send_message(to_number, message)
        
        if success:
            return {"status": "sent", "to": to_number}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")
            
    except Exception as e:
        logger.error("Send message error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))