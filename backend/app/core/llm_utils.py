"""Shared LLM utility functions.

Common operations for working with LLM responses across services.
"""

import json
import re
from typing import Any


def clean_llm_json_response(response: str) -> str:
    """
    Remove markdown code fences from LLM JSON responses.
    
    Many LLMs wrap JSON in ```json...``` fences. This strips them.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Cleaned response ready for JSON parsing
        
    Example:
        >>> raw = "```json\\n{\"key\": \"value\"}\\n```"
        >>> clean_llm_json_response(raw)
        '{"key": "value"}'
    """
    cleaned = response.strip()
    
    # Remove ```json...``` or ```...```
    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").removesuffix("```").strip()
    
    return cleaned


def parse_llm_json(response: str, default: Any = None) -> Any:
    """
    Safely parse JSON from LLM response with automatic cleaning.
    
    Args:
        response: Raw LLM response (may include markdown fences)
        default: Value to return if parsing fails
        
    Returns:
        Parsed JSON object or default value
    """
    try:
        cleaned = clean_llm_json_response(response)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try fixing common issues: single quotes → double quotes
        try:
            fixed = cleaned.replace("'", '"')
            return json.loads(fixed)
        except json.JSONDecodeError:
            return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text for logging/display.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: String to append when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_tokens_estimate(text: str) -> int:
    """
    Rough token count estimate (chars / 4).
    
    For accurate counts, use tiktoken. This is a fast approximation.
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    return len(text) // 4

