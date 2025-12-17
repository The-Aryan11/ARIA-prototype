"""
ARIA Color Analysis - Style DNA Generation
Computer Vision for skin tone and color recommendations
"""

import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
from io import BytesIO
from typing import Dict, Optional, List
import structlog

logger = structlog.get_logger()


class ColorAnalysisService:
    """
    Analyze skin tone and generate style recommendations
    """
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.5
        )
        
        # Color palettes
        self.palettes = {
            "warm": {
                "best": ["coral", "peach", "olive green", "warm red", "golden yellow", 
                         "terracotta", "cream", "bronze", "rust", "camel"],
                "avoid": ["icy blue", "bright pink", "silver", "pure white"],
                "celebrities": ["Deepika Padukone", "Priyanka Chopra", "Ranveer Singh"]
            },
            "cool": {
                "best": ["royal blue", "emerald green", "purple", "pink", "silver",
                         "navy", "lavender", "burgundy", "charcoal", "true red"],
                "avoid": ["orange", "golden yellow", "warm brown", "rust"],
                "celebrities": ["Kareena Kapoor", "Alia Bhatt", "Ranbir Kapoor"]
            },
            "neutral": {
                "best": ["jade green", "dusty pink", "teal", "soft white", "taupe",
                         "blush", "sage", "medium blue", "mauve", "soft black"],
                "avoid": ["neon colors", "very bright shades"],
                "celebrities": ["Anushka Sharma", "Katrina Kaif", "Hrithik Roshan"]
            }
        }
        
        logger.info("Color Analysis Service initialized")
    
    def analyze_from_bytes(self, image_bytes: bytes) -> Dict:
        """Analyze image from bytes"""
        try:
            image = Image.open(BytesIO(image_bytes))
            image_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            elif len(image_array.shape) == 3 and image_array.shape[2] == 4:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)
            
            return self.analyze(image_array)
            
        except Exception as e:
            logger.error("Failed to analyze image", error=str(e))
            return self._default_result()
    
    def analyze(self, image: np.ndarray) -> Dict:
        """Main analysis function"""
        
        try:
            # Convert to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect face
            results = self.face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                logger.warning("No face detected")
                return self._default_result()
            
            # Extract skin color
            skin_color = self._extract_skin_color(image, results.multi_face_landmarks[0])
            
            if skin_color is None:
                return self._default_result()
            
            # Determine undertone
            undertone = self._determine_undertone(skin_color)
            
            # Get palette
            palette = self.palettes[undertone]
            
            result = {
                "undertone": undertone,
                "best_colors": palette["best"],
                "avoid_colors": palette["avoid"],
                "celebrity_match": np.random.choice(palette["celebrities"]),
                "style_personality": self._get_style_personality(undertone),
                "confidence": 0.85
            }
            
            logger.info("Color analysis complete", undertone=undertone)
            return result
            
        except Exception as e:
            logger.error("Color analysis failed", error=str(e))
            return self._default_result()
    
    def _extract_skin_color(self, image: np.ndarray, landmarks) -> Optional[np.ndarray]:
        """Extract average skin color from face"""
        
        h, w = image.shape[:2]
        
        # Cheek region indices
        cheek_indices = [50, 101, 118, 119, 120, 280, 330, 347, 348, 349]
        
        skin_pixels = []
        
        for idx in cheek_indices:
            if idx < len(landmarks.landmark):
                landmark = landmarks.landmark[idx]
                x, y = int(landmark.x * w), int(landmark.y * h)
                
                # Sample 3x3 region
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            skin_pixels.append(image[ny, nx])
        
        if not skin_pixels:
            return None
        
        return np.mean(skin_pixels, axis=0).astype(int)
    
    def _determine_undertone(self, skin_color: np.ndarray) -> str:
        """Determine warm/cool/neutral undertone"""
        
        b, g, r = skin_color  # BGR format
        
        # Simple heuristic based on color channels
        warmth = (r - b) / 255.0
        
        if warmth > 0.15:
            return "warm"
        elif warmth < -0.05:
            return "cool"
        else:
            return "neutral"
    
    def _get_style_personality(self, undertone: str) -> str:
        """Get style personality based on undertone"""
        
        styles = {
            "warm": ["Classic Elegant", "Bohemian Chic", "Natural Earthy"],
            "cool": ["Modern Minimalist", "Glamorous Bold", "Sophisticated"],
            "neutral": ["Versatile Classic", "Timeless Elegant", "Effortless"]
        }
        
        return np.random.choice(styles.get(undertone, ["Classic"]))
    
    def _default_result(self) -> Dict:
        """Default result when analysis fails"""
        return {
            "undertone": "neutral",
            "best_colors": self.palettes["neutral"]["best"],
            "avoid_colors": self.palettes["neutral"]["avoid"],
            "celebrity_match": "Anushka Sharma",
            "style_personality": "Versatile Classic",
            "confidence": 0.5,
            "note": "Using default recommendations"
        }


# Singleton
_color_service = None


def get_color_service() -> ColorAnalysisService:
    """Get color service singleton"""
    global _color_service
    if _color_service is None:
        _color_service = ColorAnalysisService()
    return _color_service