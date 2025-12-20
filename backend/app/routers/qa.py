from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
import base64
import re

from ..services.simplifier import simplify_text
from ..services.question_generator import generate_questions
from ..services.answer_evaluator import evaluate_answer
from ..services.text_formatter import improve_formatting
from ..services.audio import synthesize_audio



router = APIRouter()


class SimplifyRequest(BaseModel):
    text: str
    language: Optional[str] = "English"
    level: Optional[str] = "default"


class SimplifyResponse(BaseModel):
    text: str


@router.post("/simplify", response_model=SimplifyResponse)
def simplify(req: SimplifyRequest) -> SimplifyResponse:
    result = simplify_text(req.text, lang=req.language or "English", level=req.level or "default")
    return SimplifyResponse(text=result)


class FormatRequest(BaseModel):
    text: str
    language: Optional[str] = "English"


@router.post("/format")
def format_text(req: FormatRequest) -> dict:
    return {"text": improve_formatting(req.text, req.language or "English")}


class AudioRequest(BaseModel):
    text: str
    language: Optional[str] = "English"


def calculate_word_timings(text: str, language: str = "English", estimated_duration: float = None) -> List[dict]:
    """
    Calculate approximate word timings based on character length with punctuation pauses.
    
    Args:
        text: The text to split into words
        language: Language for speed calibration
        estimated_duration: Total audio duration in seconds (if known)
    
    Returns:
        List of dicts with {word, start, end} for each word
    """
    # Language-specific speaking rates (characters per second)
    # Adjust these values to fine-tune highlighting speed for each language
    LANGUAGE_SPEEDS = {
        "English": 13,    # ⬅️ Adjust for English TTS speed
        "Latvian": 12,    # ⬅️ Adjust for Latvian TTS speed
        "Spanish": 13,    # ⬅️ Adjust for Spanish TTS speed (often faster)
        "Russian": 11,    # ⬅️ Adjust for Russian TTS speed
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
            '.': 0.45,  # ⬅️ Adjust for Latvian TTS pauses
            '!': 0.45,
            '?': 0.45,
            ',': 0.2,
            ';': 0.3,
            ':': 0.3,
        },
        "Spanish": {
            '.': 0.35,  # ⬅️ Spanish often has shorter pauses
            '!': 0.35,
            '?': 0.35,
            ',': 0.18,
            ';': 0.25,
            ':': 0.25,
        },
        "Russian": {
            '.': 0.5,   # ⬅️ Russian may have longer pauses
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


@router.post("/audio")
def create_audio(req: AudioRequest) -> dict:
    """
    Generate TTS audio and return as base64-encoded data with word timings.
    Frontend expects: {
        "audio": "base64string", 
        "mime": "audio/mpeg",
        "words": [{"word": "...", "start": 0.0, "end": 0.5}, ...]
    }
    """
    language = req.language or "English"
    audio_bytes = synthesize_audio(req.text, language)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    # Calculate approximate word timings with language-specific speed and punctuation pauses
    word_timings = calculate_word_timings(req.text, language)
    
    return {
        "audio": audio_b64, 
        "mime": "audio/mpeg",
        "words": word_timings
    }


class QuestionsRequest(BaseModel):
    fragment: str
    previous_questions: List[str] = []
    language: Optional[str] = "English"
    difficulty: Optional[str] = "standard"


@router.post("/questions")
def questions(req: QuestionsRequest) -> List[str]:
    return [
        str(q)
        for q in generate_questions(
            req.fragment,
            req.previous_questions,
            req.language or "English",
            req.difficulty or "standard",
        )
    ]  # type: ignore


class EvaluateRequest(BaseModel):
    fragment: str
    question: str
    answer: str
    language: Optional[str] = "English"
    userId: Optional[str] = None
    strictness: Optional[int] = 2


@router.post("/evaluate")
def evaluate(req: EvaluateRequest) -> dict:
    # Pass userId if provided for rate limiting consistency
    return evaluate_answer(
        req.fragment,
        req.question,
        req.answer,
        req.language or "English",
        user_id=req.userId,
        strictness=req.strictness or 2,
    )  # type: ignore