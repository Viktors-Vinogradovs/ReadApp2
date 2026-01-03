"""Centralized LLM initialization factory.

This module eliminates code duplication across services by providing
a single place to configure and instantiate LLM clients.
"""

from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from openai import OpenAI

from .config import settings


# Lazy-loaded singletons for performance
_llm_instances = {}


def get_gemini_llm(
    temperature: float = 0.7,
    top_p: float = 0.7,
    model_key: str = "GEMINI_QUESTION_MODEL"
) -> ChatGoogleGenerativeAI:
    """
    Get or create a Gemini LLM instance with specified configuration.
    
    Args:
        temperature: Sampling temperature (0.0-1.0)
        top_p: Nucleus sampling threshold
        model_key: Config key for model name
        
    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    cache_key = f"gemini_{temperature}_{top_p}_{model_key}"
    
    if cache_key not in _llm_instances:
        cfg = settings()
        _llm_instances[cache_key] = ChatGoogleGenerativeAI(
            model=cfg[model_key],
            api_key=cfg["GEMINI_API_KEY"],
            temperature=temperature,
            top_p=top_p,
        )
    
    return _llm_instances[cache_key]


def get_openai_client(base_url: str = "https://api.deepseek.com") -> OpenAI:
    """
    Get or create an OpenAI-compatible client (used for DeepSeek).
    
    Args:
        base_url: API endpoint base URL
        
    Returns:
        Configured OpenAI client
    """
    cache_key = f"openai_{base_url}"
    
    if cache_key not in _llm_instances:
        cfg = settings()
        _llm_instances[cache_key] = OpenAI(
            api_key=cfg["DEEPSEEK_API_KEY"],
            base_url=base_url,
        )
    
    return _llm_instances[cache_key]


def clear_llm_cache():
    """Clear all cached LLM instances. Useful for testing."""
    global _llm_instances
    _llm_instances.clear()

