"""
Simple Language Detection Model using scikit-learn
Fallback implementation when FastText is not available
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os
from typing import List, Tuple, Dict, Optional

class SimpleLanguageDetector:
    """Simple language detection using scikit-learn"""
    
    def __init__(self):
        self.model = None
        self.is_loaded = False
        self.supported_languages = [
            'English', 'French', 'German', 'Spanish', 'Italian', 
            'Portuguese', 'Dutch', 'Swedish', 'Norwegian', 'Danish',
            'Finnish', 'Polish', 'Czech', 'Hungarian', 'Romanian',
            'Bulgarian', 'Croatian', 'Serbian', 'Slovenian', 'Estonian',
            'Latvian', 'Lithuanian', 'Greek', 'Turkish', 'Russian',
            'Ukrainian', 'Belarusian', 'Arabic', 'Hebrew', 'Hindi',
            'Bengali', 'Tamil', 'Telugu', 'Marathi', 'Gujarati',
            'Kannada', 'Malayalam', 'Punjabi', 'Urdu', 'Persian',
            'Thai', 'Vietnamese', 'Indonesian', 'Malay', 'Chinese',
            'Japanese', 'Korean'
        ]
        
        # Sample training data for each language
        self.training_data = self._prepare_training_data()
        
    def _prepare_training_data(self) -> Tuple[List[str], List[str]]:
        """Prepare sample training data for different languages"""
        texts = []
        labels = []
        
        # English samples
        english_texts = [
            "Hello, how are you today?",
            "The weather is beautiful this morning.",
            "I love programming and machine learning.",
            "What time is it now?",
            "Can you help me with this task?",
            "Thank you very much for your assistance.",
            "The quick brown fox jumps over the lazy dog.",
            "Artificial intelligence is transforming the world.",
            "Education is the key to success.",
            "Technology advances rapidly every year."
        ]
        
        # French samples
        french_texts = [
            "Bonjour, comment allez-vous aujourd'hui?",
            "Le temps est magnifique ce matin.",
            "J'adore la programmation et l'apprentissage automatique.",
            "Quelle heure est-il maintenant?",
            "Pouvez-vous m'aider avec cette tâche?",
            "Merci beaucoup pour votre assistance.",
            "Le rapide renard brun saute par-dessus le chien paresseux.",
            "L'intelligence artificielle transforme le monde.",
            "L'éducation est la clé du succès.",
            "La technologie avance rapidement chaque année."
        ]
        
        # German samples
        german_texts = [
            "Hallo, wie geht es Ihnen heute?",
            "Das Wetter ist heute morgen wunderschön.",
            "Ich liebe Programmierung und maschinelles Lernen.",
            "Wie spät ist es jetzt?",
            "Können Sie mir bei dieser Aufgabe helfen?",
            "Vielen Dank für Ihre Hilfe.",
            "Der schnelle braune Fuchs springt über den faulen Hund.",
            "Künstliche Intelligenz verändert die Welt.",
            "Bildung ist der Schlüssel zum Erfolg.",
            "Die Technologie schreitet jedes Jahr schnell voran."
        ]
        
        # Spanish samples
        spanish_texts = [
            "Hola, ¿cómo estás hoy?",
            "El clima es hermoso esta mañana.",
            "Me encanta la programación y el aprendizaje automático.",
            "¿Qué hora es ahora?",
            "¿Puedes ayudarme con esta tarea?",
            "Muchas gracias por tu ayuda.",
            "El rápido zorro marrón salta sobre el perro perezoso.",
            "La inteligencia artificial está transformando el mundo.",
            "La educación es la clave del éxito.",
            "La tecnología avanza rápidamente cada año."
        ]
        
        # Add samples to training data
        for text in english_texts:
            texts.append(text)
            labels.append('English')
            
        for text in french_texts:
            texts.append(text)
            labels.append('French')
            
        for text in german_texts:
            texts.append(text)
            labels.append('German')
            
        for text in spanish_texts:
            texts.append(text)
            labels.append('Spanish')
        
        # Add some basic samples for other languages
        basic_samples = {
            'Italian': ["Ciao, come stai oggi?", "Il tempo è bello stamattina."],
            'Portuguese': ["Olá, como está hoje?", "O tempo está lindo esta manhã."],
            'Dutch': ["Hallo, hoe gaat het vandaag?", "Het weer is prachtig vanochtend."],
            'Swedish': ["Hej, hur mår du idag?", "Vädret är vackert i morse."],
            'Russian': ["Привет, как у тебя дела сегодня?", "Погода прекрасная этим утром."],
            'Chinese': ["你好，你今天好吗？", "今天早上天气很好。"],
            'Japanese': ["こんにちは、今日はお元気ですか？", "今朝は天気がいいです。"],
            'Arabic': ["مرحبا، كيف حالك اليوم؟", "الطقس جميل هذا الصباح."],
            'Hindi': ["नमस्ते, आज आप कैसे हैं?", "आज सुबह का मौसम बहुत अच्छा है।"]
        }
        
        for lang, samples in basic_samples.items():
            for text in samples:
                texts.append(text)
                labels.append(lang)
        
        return texts, labels
    
    def train(self):
        """Train the language detection model"""
        try:
            # Create a pipeline with TF-IDF vectorizer and Naive Bayes classifier
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(
                    ngram_range=(1, 3),  # Use 1-3 grams
                    lowercase=True,
                    stop_words=None,  # Keep stop words as they can be language-specific
                    min_df=1,
                    max_features=10000
                )),
                ('classifier', MultinomialNB(alpha=0.1))
            ])
            
            # Train the model
            texts, labels = self.training_data
            self.model.fit(texts, labels)
            self.is_loaded = True
            
            print(f"Model trained successfully on {len(texts)} samples")
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict(self, text: str) -> Tuple[str, float]:
        """Predict language of given text"""
        if not self.is_loaded or not self.model:
            return "Unknown", 0.0
        
        try:
            # Make prediction
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            
            # Get confidence score
            confidence = max(probabilities)
            
            return prediction, confidence
            
        except Exception as e:
            print(f"Error predicting language: {e}")
            return "Unknown", 0.0
    
    def predict_with_confidence_check(self, text: str, k: int = 3) -> Tuple[List[Dict], str, str, float]:
        """Predict language with confidence check and return top k predictions"""
        if not self.is_loaded or not self.model:
            return [], "Unknown", "error", 0.0
        
        try:
            import time
            start_time = time.time()
            
            # Get predictions and probabilities
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            
            # Get class names (languages)
            classes = self.model.classes_
            
            # Create list of predictions with confidence scores
            predictions = []
            for i, lang in enumerate(classes):
                predictions.append({
                    "language": lang,
                    "confidence": float(probabilities[i])
                })
            
            # Sort by confidence
            predictions.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Get top k predictions
            top_predictions = predictions[:k]
            
            # Determine script (simplified)
            script = self._detect_script(text)
            
            # Determine status based on confidence
            max_confidence = top_predictions[0]["confidence"] if top_predictions else 0.0
            if max_confidence > 0.7:
                status = "success"
            elif max_confidence > 0.4:
                status = "low_confidence"
            else:
                status = "unknown"
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return top_predictions, script, status, processing_time
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return [], "Unknown", "error", 0.0
    
    def _detect_script(self, text: str) -> str:
        """Simple script detection"""
        if not text:
            return "Unknown"
        
        # Check for common scripts
        if any('\u0400' <= char <= '\u04FF' for char in text):
            return "Cyrillic"
        elif any('\u0600' <= char <= '\u06FF' for char in text):
            return "Arabic"
        elif any('\u4E00' <= char <= '\u9FFF' for char in text):
            return "CJK"
        elif any('\u0900' <= char <= '\u097F' for char in text):
            return "Devanagari"
        elif any('\u0590' <= char <= '\u05FF' for char in text):
            return "Hebrew"
        elif any('\u0E00' <= char <= '\u0E7F' for char in text):
            return "Thai"
        else:
            return "Latin"
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        if self.is_loaded and self.model:
            return list(self.model.classes_)
        return self.supported_languages
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        if self.is_loaded and self.model:
            try:
                with open(filepath, 'wb') as f:
                    pickle.dump(self.model, f)
                print(f"Model saved to {filepath}")
                return True
            except Exception as e:
                print(f"Error saving model: {e}")
                return False
        return False
    
    def load_model(self, filepath: str) -> bool:
        """Load a trained model"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_loaded = True
                print(f"Model loaded from {filepath}")
                return True
            else:
                print(f"Model file not found: {filepath}")
                return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

# Global model instance
simple_detector = SimpleLanguageDetector()

def get_simple_model():
    """Get the global simple model instance"""
    return simple_detector

def initialize_simple_model(model_path: str = None) -> bool:
    """Initialize the simple model"""
    global simple_detector
    
    # Try to load existing model
    if model_path and os.path.exists(model_path):
        if simple_detector.load_model(model_path):
            return True
    
    # Train new model
    if simple_detector.train():
        # Save the trained model for future use
        if model_path:
            simple_detector.save_model(model_path)
        return True
    
    return False
