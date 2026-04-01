"""
Language detection model wrapper with FastText and scikit-learn fallback
"""

import os
import time
import logging
from typing import List, Tuple, Dict, Optional

from config import settings
from utils import preprocess_text, detect_script, map_language_code, format_confidence
from simple_model import get_simple_model, initialize_simple_model

logger = logging.getLogger(__name__)


class FastTextLanguageDetector:
    """
    FastText-based language detection model
    """
    
    def __init__(self):
        """Initialize the language detector"""
        self.model = None
        self.model_path = None
        self.is_loaded = False
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        
        # Language code mapping (FastText codes to full names)
        self.language_mapping = {
            '__label__en': 'English',
            '__label__fr': 'French',
            '__label__de': 'German',
            '__label__es': 'Spanish',
            '__label__it': 'Italian',
            '__label__pt': 'Portuguese',
            '__label__ru': 'Russian',
            '__label__ar': 'Arabic',
            '__label__hi': 'Hindi',
            '__label__ta': 'Tamil',
            '__label__te': 'Telugu',
            '__label__bn': 'Bengali',
            '__label__mr': 'Marathi',
            '__label__gu': 'Gujarati',
            '__label__kn': 'Kannada',
            '__label__ml': 'Malayalam',
            '__label__pa': 'Punjabi',
            '__label__or': 'Odia',
            '__label__as': 'Assamese',
            '__label__zh': 'Chinese',
            '__label__ja': 'Japanese',
            '__label__ko': 'Korean',
            '__label__th': 'Thai',
            '__label__vi': 'Vietnamese',
            '__label__id': 'Indonesian',
            '__label__ms': 'Malay',
            '__label__tl': 'Filipino',
            '__label__ne': 'Nepali',
            '__label__si': 'Sinhala',
            '__label__my': 'Myanmar',
            '__label__km': 'Khmer',
            '__label__lo': 'Lao',
            '__label__ka': 'Georgian',
            '__label__am': 'Amharic',
            '__label__sw': 'Swahili',
            '__label__zu': 'Zulu',
            '__label__af': 'Afrikaans',
            '__label__is': 'Icelandic',
            '__label__mt': 'Maltese',
            '__label__cy': 'Welsh',
            '__label__ga': 'Irish',
            '__label__gd': 'Scottish Gaelic',
            '__label__eu': 'Basque',
            '__label__ca': 'Catalan',
            '__label__gl': 'Galician',
            '__label__hr': 'Croatian',
            '__label__sr': 'Serbian',
            '__label__sl': 'Slovenian',
            '__label__bg': 'Bulgarian',
            '__label__cs': 'Czech',
            '__label__sk': 'Slovak',
            '__label__pl': 'Polish',
            '__label__uk': 'Ukrainian',
            '__label__be': 'Belarusian',
            '__label__et': 'Estonian',
            '__label__lv': 'Latvian',
            '__label__lt': 'Lithuanian',
            '__label__mk': 'Macedonian',
            '__label__ro': 'Romanian',
            '__label__hu': 'Hungarian',
            '__label__fi': 'Finnish',
            '__label__sv': 'Swedish',
            '__label__nb': 'Norwegian Bokmål',
            '__label__da': 'Danish',
            '__label__nl': 'Dutch',
            '__label__tr': 'Turkish',
            '__label__az': 'Azerbaijani',
            '__label__kk': 'Kazakh',
            '__label__ky': 'Kyrgyz',
            '__label__uz': 'Uzbek',
            '__label__tg': 'Tajik',
            '__label__mn': 'Mongolian',
            '__label__hy': 'Armenian',
            '__label__he': 'Hebrew',
            '__label__ur': 'Urdu',
            '__label__fa': 'Persian',
            '__label__ps': 'Pashto',
            '__label__sd': 'Sindhi',
            '__label__ku': 'Kurdish',
            '__label__yi': 'Yiddish'
        }
    
    def load_model(self, model_path: str) -> bool:
        """
        Load FastText model from file
        
        Args:
            model_path: Path to the FastText model file
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            # Try to import fasttext
            import fasttext
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
            
            logger.info(f"Loading FastText model from {model_path}")
            start_time = time.time()
            
            self.model = fasttext.load_model(model_path)
            self.model_path = model_path
            self.is_loaded = True
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
            
            return True
            
        except ImportError:
            logger.error("FastText library not installed. Install with: pip install fasttext-wheel")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def predict(self, text: str, k: int = 3) -> Tuple[List[Dict[str, float]], str, float]:
        """
        Predict language for given text
        
        Args:
            text: Input text to analyze
            k: Number of top predictions to return
            
        Returns:
            Tuple of (predictions, script, processing_time)
        """
        if not self.is_loaded:
            # Fallback to simple model
            simple_detector = get_simple_model()
            if simple_detector.is_loaded:
                predictions, script, _, processing_time = simple_detector.predict_with_confidence_check(text, k)
                return predictions, script, processing_time
            else:
                raise RuntimeError("No model loaded. Call load_model() first.")
        
        start_time = time.time()
        
        # Preprocess text
        preprocessed_text = preprocess_text(text)
        
        # Detect script
        script = detect_script(preprocessed_text)
        
        # Predict using FastText
        try:
            # FastText predict returns (labels, probabilities)
            labels, probabilities = self.model.predict(preprocessed_text, k=k)
            
            # Convert to list of (language, confidence) tuples
            predictions = []
            for label, prob in zip(labels, probabilities):
                # Remove __label__ prefix and map to full language name
                language_code = label.replace('__label__', '')
                language_name = self.language_mapping.get(label, language_code.upper())
                
                predictions.append({
                    'language': language_name,
                    'confidence': format_confidence(prob)
                })
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return predictions, script, processing_time
            
        except Exception as e:
            logger.error(f"FastText prediction failed: {e}")
            # Fallback to simple model
            simple_detector = get_simple_model()
            if simple_detector.is_loaded:
                predictions, script, _, processing_time = simple_detector.predict_with_confidence_check(text, k)
                return predictions, script, processing_time
            else:
                raise RuntimeError(f"Prediction failed: {e}")
    
    def predict_with_confidence_check(self, text: str, k: int = 3) -> Tuple[List[Dict[str, float]], str, str, float]:
        """
        Predict language with confidence threshold check
        
        Args:
            text: Input text to analyze
            k: Number of top predictions to return
            
        Returns:
            Tuple of (predictions, script, status, processing_time)
        """
        predictions, script, processing_time = self.predict(text, k)
        
        # Check confidence threshold
        if not predictions or predictions[0]['confidence'] < self.confidence_threshold:
            status = "uncertain"
        else:
            status = "success"
        
        return predictions, script, status, processing_time
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages
        
        Returns:
            List of supported language names
        """
        if self.is_loaded:
            return list(self.language_mapping.values())
        else:
            # Fallback to simple model
            simple_detector = get_simple_model()
            if simple_detector.is_loaded:
                return simple_detector.get_supported_languages()
            return []
    
    def benchmark_model(self, test_texts: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Benchmark the model with test texts
        
        Args:
            test_texts: Dictionary of language to test texts
            
        Returns:
            Dictionary with benchmark metrics
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        correct_predictions = 0
        total_predictions = 0
        processing_times = []
        
        for true_language, texts in test_texts.items():
            for text in texts:
                try:
                    predictions, _, processing_time = self.predict(text, k=1)
                    predicted_language = predictions[0]['language']
                    
                    # Check if prediction matches true language
                    if predicted_language.lower() == true_language.lower():
                        correct_predictions += 1
                    
                    total_predictions += 1
                    processing_times.append(processing_time)
                    
                except Exception as e:
                    logger.error(f"Error benchmarking text '{text}': {e}")
                    continue
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            'accuracy': accuracy,
            'avg_processing_time_ms': avg_processing_time,
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions
        }


# Global model instance (singleton pattern)
_language_detector = None


def get_model() -> FastTextLanguageDetector:
    """
    Get the global model instance
    
    Returns:
        FastTextLanguageDetector instance
    """
    global _language_detector
    if _language_detector is None:
        _language_detector = FastTextLanguageDetector()
    return _language_detector


def initialize_model(model_path: str = None) -> bool:
    """
    Initialize the global model instance with FastText or fallback to scikit-learn
    
    Args:
        model_path: Path to FastText model file
        
    Returns:
        True if model loaded successfully, False otherwise
    """
    if model_path is None:
        model_path = settings.get_model_path()
    
    detector = get_model()
    
    # Try to load FastText model first
    if detector.load_model(model_path):
        return True
    
    # Fallback to simple scikit-learn model
    logger.warning("FastText model not available, falling back to scikit-learn model")
    simple_model_path = model_path.replace('.bin', '_simple.pkl')
    return initialize_simple_model(simple_model_path)
