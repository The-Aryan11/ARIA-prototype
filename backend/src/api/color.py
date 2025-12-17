"""
ARIA Color Analysis API - Style DNA Endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import structlog
import base64

from ..services.color_analysis import get_color_service
from ..services.session_service import get_session_service

logger = structlog.get_logger()
router = APIRouter(prefix="/color", tags=["Color Analysis"])


class ColorAnalysisResponse(BaseModel):
    """Color analysis result"""
    undertone: str
    best_colors: List[str]
    avoid_colors: List[str]
    celebrity_match: str
    style_personality: str
    confidence: float


class Base64ImageRequest(BaseModel):
    """Request with base64 encoded image"""
    user_id: str
    image_base64: str


@router.post("/analyze", response_model=ColorAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze uploaded image for color recommendations
    
    Upload a selfie to get personalized color palette.
    """
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Analyze
        color_service = get_color_service()
        result = color_service.analyze_from_bytes(image_bytes)
        
        logger.info("Color analysis completed", undertone=result["undertone"])
        
        return ColorAnalysisResponse(**result)
        
    except Exception as e:
        logger.error("Color analysis error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-base64", response_model=ColorAnalysisResponse)
async def analyze_base64_image(request: Base64ImageRequest):
    """
    Analyze base64 encoded image
    
    For web/mobile apps that send image as base64 string.
    """
    
    try:
        # Decode base64
        image_bytes = base64.b64decode(request.image_base64)
        
        # Analyze
        color_service = get_color_service()
        result = color_service.analyze_from_bytes(image_bytes)
        
        # Save to session if user_id provided
        if request.user_id:
            sessions = get_session_service()
            await sessions.update_style_dna(request.user_id, result)
        
        logger.info("Color analysis completed", 
                   undertone=result["undertone"],
                   user_id=request.user_id[:10] + "..." if request.user_id else None)
        
        return ColorAnalysisResponse(**result)
        
    except Exception as e:
        logger.error("Color analysis error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/style-dna/{user_id}")
async def get_style_dna(user_id: str):
    """
    Get stored Style DNA for a user
    """
    
    try:
        sessions = get_session_service()
        session = await sessions.get_session(user_id)
        
        if not session or not session.get("style_dna"):
            raise HTTPException(
                status_code=404, 
                detail="Style DNA not found. Upload a selfie first!"
            )
        
        return session["style_dna"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get Style DNA error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/palettes")
async def get_color_palettes():
    """
    Get all color palettes for reference
    """
    
    color_service = get_color_service()
    return {
        "palettes": color_service.palettes,
        "description": {
            "warm": "Golden, peachy, olive tones - best with earth colors",
            "cool": "Pink, blue, silver tones - best with jewel colors",
            "neutral": "Balanced tones - versatile with most colors"
        }
    }