from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Dict
import base64
import logging

from ..services.simplifier import simplify_text
from ..services.question_generator import generate_questions, generate_questions_batch
from ..services.answer_evaluator import evaluate_answer
from ..services.text_formatter import improve_formatting
from ..services.audio import synthesize_audio
from ..services.audio_utils import calculate_word_timings

logger = logging.getLogger(__name__)



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
    try:
        return [
            str(q)
            for q in generate_questions(
                req.fragment,
                req.previous_questions,
                req.language or "English",
                req.difficulty or "standard",
            )
        ]  # type: ignore
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Question generation failed: {error_msg}")
        
        # Return 429 for rate limits, 500 for other errors
        if "rate limit" in error_msg.lower() or "⏳" in error_msg:
            raise HTTPException(status_code=429, detail=error_msg)
        elif "API key" in error_msg or "🔑" in error_msg:
            raise HTTPException(status_code=401, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        logger.error(f"Unexpected error in questions endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class BatchQuestionsRequest(BaseModel):
    text_name: str
    fragments: List[str]
    language: Optional[str] = "English"
    difficulty: Optional[str] = "standard"


class BatchQuestionsResponse(BaseModel):
    questions_by_fragment: Dict[int, List[str]]
    total_fragments: int
    total_api_calls: int


@router.post("/questions/batch", response_model=BatchQuestionsResponse)
def batch_questions(req: BatchQuestionsRequest) -> BatchQuestionsResponse:
    """
    Generate questions for all fragments in a single or few API calls.
    Provides full story context to the LLM for better question quality.
    """
    try:
        logger.info(f"Batch question generation for '{req.text_name}' ({len(req.fragments)} fragments)")
        
        result = generate_questions_batch(
            fragments=req.fragments,
            language=req.language or "English",
            difficulty=req.difficulty or "standard",
            text_name=req.text_name
        )
        
        logger.info(f"✅ Generated questions for {len(result['questions_by_fragment'])} fragments")
        
        return BatchQuestionsResponse(
            questions_by_fragment=result['questions_by_fragment'],
            total_fragments=len(req.fragments),
            total_api_calls=result.get('api_calls', 1)
        )
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Batch question generation failed: {error_msg}")
        
        if "rate limit" in error_msg.lower() or "⏳" in error_msg:
            raise HTTPException(status_code=429, detail=error_msg)
        elif "API key" in error_msg or "🔑" in error_msg:
            raise HTTPException(status_code=401, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        logger.error(f"Unexpected error in batch questions endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class EvaluateRequest(BaseModel):
    fragment: str
    question: str
    answer: str
    language: Optional[str] = "English"
    userId: Optional[str] = None
    strictness: Optional[int] = 2


@router.post("/evaluate")
def evaluate(req: EvaluateRequest) -> dict:
    try:
        # Pass userId if provided for rate limiting consistency
        return evaluate_answer(
            req.fragment,
            req.question,
            req.answer,
            req.language or "English",
            user_id=req.userId,
            strictness=req.strictness or 2,
        )  # type: ignore
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Answer evaluation failed: {error_msg}")
        
        # Return 429 for rate limits, 500 for other errors
        if "rate limit" in error_msg.lower() or "⏳" in error_msg:
            raise HTTPException(status_code=429, detail=error_msg)
        elif "API key" in error_msg or "🔑" in error_msg:
            raise HTTPException(status_code=401, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        logger.error(f"Unexpected error in evaluate endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")