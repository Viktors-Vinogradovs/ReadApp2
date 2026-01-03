"""Audio-related utility functions.

Extracted from routers/qa.py to maintain single responsibility principle.
"""

import re
from typing import List, Dict, Optional


def calculate_word_timings(
    text: str,
    language: str = "English",
    estimated_duration: Optional[float] = None
) -> List[Dict[str, any]]:
    """
    Calculate approximate word timings based on character length with punctuation pauses.
    
    This generates timing data for synchronized text highlighting during audio playback.
    
    Args:
        text: The text to split into words
        language: Language for speed calibration
        estimated_duration: Total audio duration in seconds (if known)
    
    Returns:
        List of dicts with {word, start, end} for each word
        
    Example:
        >>> timings = calculate_word_timings("Hello world.", "English")
        >>> timings[0]
        {'word': 'Hello', 'start': 0.0, 'end': 0.38}
    """
    # Language-specific speaking rates (characters per second)
    # Adjust these values to fine-tune highlighting speed for each language
    LANGUAGE_SPEEDS = {
        "English": 13,
        "Latvian": 12,
        "Spanish": 13,
        "Russian": 11,
    }
    
    # Language-specific punctuation pause durations (in seconds)
    # Each language's TTS may have different natural pause lengths
    PUNCTUATION_PAUSES = {
        "English": {
            '.': 0.4,   # Period - longer pause
            '!': 0.4,   # Exclamation - longer pause
            '?': 0.4,   # Question - longer pause
            ',': 0.2,   # Comma - shorter pause
            ';': 0.3,   # Semicolon - medium pause
            ':': 0.3,   # Colon - medium pause
        },
        "Latvian": {
            '.': 0.45,
            '!': 0.45,
            '?': 0.45,
            ',': 0.2,
            ';': 0.3,
            ':': 0.3,
        },
        "Spanish": {
            '.': 0.35,
            '!': 0.35,
            '?': 0.35,
            ',': 0.18,
            ';': 0.25,
            ':': 0.25,
        },
        "Russian": {
            '.': 0.5,
            '!': 0.5,
            '?': 0.5,
            ',': 0.25,
            ';': 0.35,
            ':': 0.35,
        },
    }
    
    # Split into words, preserving punctuation
    words = re.findall(r'\S+', text)
    
    if not words:
        return []
    
    # Get language-specific speed and pauses
    chars_per_second = LANGUAGE_SPEEDS.get(language, 13)
    language_pauses = PUNCTUATION_PAUSES.get(language, PUNCTUATION_PAUSES["English"])
    
    # Calculate character count for each word and detect punctuation
    word_data = []
    total_chars = 0
    total_pause_time = 0.0
    
    for word in words:
        # Count only alphanumeric characters for timing
        char_count = len(re.sub(r'[^\w]', '', word))
        
        # Check if word ends with punctuation (using language-specific pauses)
        pause_duration = 0.0
        for punct, pause in language_pauses.items():
            if word.endswith(punct):
                pause_duration = pause
                break
        
        word_data.append({
            'word': word,
            'chars': max(char_count, 1),  # Minimum 1 char
            'pause': pause_duration
        })
        total_chars += word_data[-1]['chars']
        total_pause_time += pause_duration
    
    # Estimate duration if not provided
    if estimated_duration is None:
        # Base duration from characters + pause time
        base_duration = total_chars / chars_per_second
        estimated_duration = base_duration + total_pause_time
    
    # Calculate timing for each word based on character proportion
    timings = []
    current_time = 0.0
    
    # Duration available for actual words (excluding pauses)
    words_duration = estimated_duration - total_pause_time
    
    for wd in word_data:
        # Time for this word based on its character proportion
        word_duration = (wd['chars'] / total_chars) * words_duration if total_chars > 0 else 0.1
        
        timings.append({
            'word': wd['word'],
            'start': round(current_time, 2),
            'end': round(current_time + word_duration, 2)
        })
        
        # Move to next word, including any pause after this word
        current_time += word_duration + wd['pause']
    
    return timings

