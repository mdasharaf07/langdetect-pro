"""
Utility functions for text preprocessing and script detection
"""

import re
import unicodedata
from typing import Dict, List, Tuple


# Language code to full name mapping
LANGUAGE_MAPPING = {
    'af': 'Afrikaans',
    'ar': 'Arabic',
    'bg': 'Bulgarian',
    'bn': 'Bengali',
    'ca': 'Catalan',
    'cs': 'Czech',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'el': 'Greek',
    'en': 'English',
    'es': 'Spanish',
    'et': 'Estonian',
    'fa': 'Persian',
    'fi': 'Finnish',
    'fr': 'French',
    'gu': 'Gujarati',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hr': 'Croatian',
    'hu': 'Hungarian',
    'id': 'Indonesian',
    'is': 'Icelandic',
    'it': 'Italian',
    'ja': 'Japanese',
    'kn': 'Kannada',
    'ko': 'Korean',
    'lt': 'Lithuanian',
    'lv': 'Latvian',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'ne': 'Nepali',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'pa': 'Punjabi',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tl': 'Tagalog',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'vi': 'Vietnamese',
    'zh': 'Chinese',
    'zu': 'Zulu'
}

# Unicode ranges for script detection
SCRIPT_RANGES = {
    'Latin': [(0x0000, 0x007F), (0x0080, 0x00FF), (0x0100, 0x017F), (0x0180, 0x024F)],
    'Cyrillic': [(0x0400, 0x04FF), (0x0500, 0x052F), (0x1C80, 0x1C8F)],
    'Arabic': [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
    'Devanagari': [(0x0900, 0x097F)],
    'Bengali': [(0x0980, 0x09FF)],
    'Gurmukhi': [(0x0A00, 0x0A7F)],
    'Gujarati': [(0x0A80, 0x0AFF)],
    'Oriya': [(0x0B00, 0x0B7F)],
    'Tamil': [(0x0B80, 0x0BFF)],
    'Telugu': [(0x0C00, 0x0C7F)],
    'Kannada': [(0x0C80, 0x0CFF)],
    'Malayalam': [(0x0D00, 0x0D7F)],
    'Sinhala': [(0x0D80, 0x0DFF)],
    'Thai': [(0x0E00, 0x0E7F)],
    'Lao': [(0x0E80, 0x0EFF)],
    'Tibetan': [(0x0F00, 0x0FFF)],
    'Myanmar': [(0x1000, 0x109F)],
    'Georgian': [(0x10A0, 0x10FF)],
    'Hangul': [(0xAC00, 0xD7AF), (0x1100, 0x11FF), (0x3130, 0x318F)],
    'Ethiopic': [(0x1200, 0x137F), (0x1380, 0x139F), (0x2D80, 0x2DDF)],
    'Hebrew': [(0x0590, 0x05FF), (0xFB1D, 0xFB4F)],
    'Armenian': [(0x0530, 0x058F)],
    'Greek': [(0x0370, 0x03FF), (0x1F00, 0x1FFF)],
    'CJK': [(0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0x20000, 0x2A6DF)],
    'Hiragana': [(0x3040, 0x309F)],
    'Katakana': [(0x30A0, 0x30FF)],
    'HangulJamo': [(0x1100, 0x11FF), (0x3130, 0x318F)],
}


def preprocess_text(text: str) -> str:
    """
    Preprocess text for language detection
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    # Remove numbers (keep as they might be language-specific)
    # text = re.sub(r'\d+', '', text)
    
    # Remove excessive punctuation but keep basic ones
    text = re.sub(r'[^\w\s\.,!?;:]', ' ', text)
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Strip and return
    return text.strip()


def detect_script(text: str) -> str:
    """
    Detect the script of the given text using Unicode ranges
    
    Args:
        text: Input text
        
    Returns:
        Detected script name
    """
    script_counts = {script: 0 for script in SCRIPT_RANGES}
    
    for char in text:
        char_code = ord(char)
        
        for script, ranges in SCRIPT_RANGES.items():
            for start, end in ranges:
                if start <= char_code <= end:
                    script_counts[script] += 1
                    break
    
    # Find the script with the most characters
    if not any(script_counts.values()):
        return "Unknown"
    
    max_script = max(script_counts, key=script_counts.get)
    
    # If very few characters match, return Unknown
    if script_counts[max_script] < len(text) * 0.1:
        return "Unknown"
    
    return max_script


def map_language_code(language_code: str) -> str:
    """
    Map FastText language code to full language name
    
    Args:
        language_code: FastText language code (e.g., 'en')
        
    Returns:
        Full language name (e.g., 'English')
    """
    # Remove '__label__' prefix if present
    if language_code.startswith('__label__'):
        language_code = language_code[9:]
    
    return LANGUAGE_MAPPING.get(language_code, language_code.title())


def clean_fasttext_label(label: str) -> str:
    """
    Clean FastText label by removing __label__ prefix
    
    Args:
        label: FastText label
        
    Returns:
        Cleaned label
    """
    if label.startswith('__label__'):
        return label[9:]
    return label


def format_confidence(confidence: float) -> float:
    """
    Format confidence score to appropriate precision
    
    Args:
        confidence: Raw confidence score
        
    Returns:
        Formatted confidence score
    """
    return round(confidence, 4)


def validate_input_text(text: str) -> Tuple[bool, str]:
    """
    Validate input text for language detection
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Text cannot be empty"
    
    text = text.strip()
    
    if len(text) < 3:
        return False, "Text must be at least 3 characters long"
    
    if len(text) > 10000:
        return False, "Text is too long (maximum 10000 characters)"
    
    # Check if text contains only whitespace or punctuation
    if re.match(r'^[\s\.,!?;:]+$', text):
        return False, "Text must contain meaningful characters"
    
    return True, ""


def get_sample_texts() -> Dict[str, List[str]]:
    """
    Get sample texts for testing different languages
    
    Returns:
        Dictionary of language codes to sample texts
    """
    return {
        'English': [
            "Hello, how are you today? I hope you're having a wonderful day!",
            "The weather is beautiful this morning.",
            "I love programming and machine learning."
        ],
        'French': [
            "Bonjour, comment allez-vous aujourd'hui?",
            "Le temps est magnifique ce matin.",
            "J'adore la programmation et l'apprentissage automatique."
        ],
        'German': [
            "Hallo, wie geht es Ihnen heute?",
            "Das Wetter ist heute Morgen wunderschön.",
            "Ich liebe Programmierung und maschinelles Lernen."
        ],
        'Spanish': [
            "¡Hola, ¿cómo estás hoy?",
            "El tiempo está hermoso esta mañana.",
            "Me encanta la programación y el aprendizaje automático."
        ],
        'Tamil': [
            "வணக்கம், நீங்கள் இன்று எப்படி இருக்கிறீர்கள்?",
            "இன்று காலை வானிலை அழகாக உள்ளது.",
            "நான் நிரலாக்கம் மற்றும் இயந்திர கற்றலை விரும்புகிறேன்."
        ],
        'Hindi': [
            "नमस्ते, आज आप कैसे हैं?",
            "आज सुबह का मौसम बहुत खूबसूरत है।",
            "मुझे प्रोग्रामिंग और मशीन लर्निंग पसंद है।"
        ],
        'Arabic': [
            "مرحبا، كيف حالك اليوم؟",
            "الطقس جميل هذا الصباح.",
            "أحب البرمجة والتعلم الآلي."
        ],
        'Chinese': [
            "你好，你今天怎么样？",
            "今天早上天气很好。",
            "我喜欢编程和机器学习。"
        ],
        'Japanese': [
            "こんにちは、今日はお元気ですか？",
            "今朝は天気がいいですね。",
            "プログラミングと機械学習が好きです。"
        ]
    }
