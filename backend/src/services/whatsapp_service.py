"""
ARIA WhatsApp Service - Twilio Integration
Handles sending and receiving WhatsApp messages
"""

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from typing import Optional
import structlog
import httpx

from ..core.config import settings

logger = structlog.get_logger()


class WhatsAppService:
    """
    WhatsApp messaging via Twilio
    """
    
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER
        logger.info("WhatsApp service initialized")
    
    async def send_message(
        self, 
        to_number: str, 
        message: str
    ) -> bool:
        """Send WhatsApp message"""
        
        try:
            # Ensure proper format
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            # Send via Twilio
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info("WhatsApp message sent", to=to_number[:15] + "...")
            return True
            
        except Exception as e:
            logger.error("Failed to send WhatsApp message", error=str(e))
            return False
    
    async def send_media(
        self,
        to_number: str,
        message: str,
        media_url: str
    ) -> bool:
        """Send WhatsApp message with media"""
        
        try:
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number,
                media_url=[media_url]
            )
            
            logger.info("WhatsApp media sent", to=to_number[:15] + "...")
            return True
            
        except Exception as e:
            logger.error("Failed to send WhatsApp media", error=str(e))
            return False
    
    async def download_media(self, media_url: str) -> Optional[bytes]:
        """Download media from Twilio"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    media_url,
                    auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                    follow_redirects=True
                )
                response.raise_for_status()
                return response.content
                
        except Exception as e:
            logger.error("Failed to download media", error=str(e))
            return None
    
    def create_response(self, message: str) -> str:
        """Create TwiML response"""
        response = MessagingResponse()
        response.message(message)
        return str(response)


# Singleton
_whatsapp_service = None


def get_whatsapp_service() -> WhatsAppService:
    """Get WhatsApp service singleton"""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service