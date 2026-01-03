"""Application configuration helpers."""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str | None = None) -> str:
    """Fetch configuration values from environment or .env file."""

    value = os.getenv(key, default)

    if value is not None:
        return value

    raise ValueError(
        f"Secret '{key}' not found. Set it in your environment or .env file."
    )


@lru_cache(maxsize=None)
def settings() -> dict:
    return {
        "GEMINI_API_KEY": get_secret("GEMINI_API_KEY"),
        "GEMINI_AUDIO_API_KEY": get_secret("GEMINI_AUDIO_API_KEY"),
        "DEEPSEEK_API_KEY": get_secret("DEEPSEEK_API_KEY"),
        "HF_API_TOKEN": get_secret("HF_API_TOKEN"),
        "GEMINI_QUESTION_MODEL": "gemini-2.5-flash-lite",
        "GEMINI_SPLITTER_MODEL": "gemini-2.5-flash-lite",
        "GEMINI_AUDIO_MODEL": "gemini-2.5-flash-lite",
        "OPENAI_TTS_MODEL": "tts-1",
        "OPENAI_TTS_HD_MODEL": "tts-1-hd",
        "OPENAI_DEFAULT_VOICE": "nova",
        "OPENAI_TTS_SPEED": 1.0,
        "GOOGLE_CLOUD_PROJECT_ID": "",
        "GOOGLE_TTS_SAMPLE_RATE": 22050,
        "GOOGLE_TTS_SPEAKING_RATE": 1.0,
        "GOOGLE_TTS_PITCH": 0.0,
    }


