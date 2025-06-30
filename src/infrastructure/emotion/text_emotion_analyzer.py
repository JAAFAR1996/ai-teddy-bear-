"""Text-based emotion analysis infrastructure."""

import structlog
from typing import Dict, List, Optional
from transformers import pipeline

logger = structlog.get_logger(__name__)


class TextEmotionAnalyzer:
    """Infrastructure component for text emotion analysis."""
    
    def __init__(self):
        self.text_analyzer = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the transformer model."""
        try:
            self.text_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            logger.info(" Text emotion model loaded")
        except Exception as e:
            logger.error(f" Failed to load model: {e}")
            self.text_analyzer = None
    
    async def analyze_text(self, text: str) -> Optional[Dict[str, float]]:
        """Analyze text and return emotion scores."""
        if not self.text_analyzer or not text.strip():
            return None
        
        try:
            predictions = self.text_analyzer(text)
            
            emotion_scores = {}
            for pred in predictions[0]:
                emotion = pred['label'].lower()
                score = pred['score']
                emotion_scores[emotion] = score
            
            return emotion_scores
            
        except Exception as e:
            logger.error(f" Text analysis failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if the analyzer is available."""
        return self.text_analyzer is not None
