import json
import re

import google.generativeai as genai
import tiktoken

from backend.app.core.config import settings


_cfg = settings()

genai.configure(api_key=_cfg["GEMINI_API_KEY"])
model = genai.GenerativeModel(_cfg["GEMINI_SPLITTER_MODEL"])
encoding = tiktoken.get_encoding("cl100k_base")


def num_tokens(text: str) -> int:
    return len(encoding.encode(text))


def _fallback_simple_split(text: str, max_chars: int = 800) -> list[str]:
    """
    Fallback splitter used when Gemini / JSON parsing fails.
    - Split by blank lines into paragraphs.
    - Merge paragraphs up to max_chars.
    """
    text = text.strip()
    if not text:
        return []
    
    # Paragraphs separated by blank lines
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return [text]
    
    fragments: list[str] = []
    current = ""
    
    for para in paragraphs:
        # +2 for the '\n\n' we might add
        if len(current) + len(para) + 2 <= max_chars:
            if current:
                current += "\n\n" + para
            else:
                current = para
        else:
            if current:
                fragments.append(current)
            current = para
    
    if current:
        fragments.append(current)
    
    return fragments


def split_text_to_fragments(full_text: str, target_tokens: int = 400, max_tokens: int = 5000) -> list[str]:
    """
    Split a long story into 2–8 logical fragments using Gemini.
    On any error or invalid JSON, fall back to a simple rule-based splitter.
    """
    full_text = full_text.strip()
    if not full_text:
        return []
    
    # For short texts, don't bother the LLM
    if len(full_text) < 800:
        return [full_text]
    
    total_tokens = num_tokens(full_text)
    
    if total_tokens > max_tokens:
        print(f"Text exceeds max limit ({max_tokens} tokens). Found: {total_tokens}")
        # Still try to split it with fallback
        return _fallback_simple_split(full_text, max_chars=900)
    
    target_tokens = max(100, min(target_tokens, 900))
    soft_min = max(60, int(target_tokens * 0.65))
    soft_max = int(target_tokens * 1.4)
    
    prompt = f"""
You are a precise text splitter for a reading comprehension app.
Your job: split the story below into 2–8 logical fragments that are comfortable to read on screen.

Rules:
- Keep sentences intact.
- Keep dialogue lines together.
- Don't cut in the middle of a sentence.
- Aim for **{target_tokens} tokens** per fragment.
- Stay within **{soft_min} – {soft_max} tokens** whenever possible.
- Each fragment should be roughly similar length, but meaning comes first.

Return ONLY a valid JSON object:
{{"fragments": ["first fragment here", "second fragment here"]}}

No markdown, no extra keys, no comments.

Story:
{full_text}
""".strip()
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        print("🟡 Raw LLM Response:", raw_text[:200] + "..." if len(raw_text) > 200 else raw_text)
        
        # Strip ```json ``` wrappers if present
        if raw_text.startswith("```json"):
            raw_text = raw_text.removeprefix("```json").removesuffix("```").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.removeprefix("```").removesuffix("```").strip()
        
        try:
            fragments_json = json.loads(raw_text)
        except json.JSONDecodeError as jde:
            print("JSON Decode Error:", jde)
            print("Raw response was:", raw_text[:500] + "..." if len(raw_text) > 500 else raw_text)
            
            # Second attempt: escape backslashes and control chars
            try:
                fixed_text = (
                    raw_text
                    .replace("\\", "\\\\")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t")
                )
                fragments_json = json.loads(fixed_text)
                print("🟢 Fixed JSON after escape sequence repair")
            except json.JSONDecodeError:
                print("🔴 Could not fix JSON - falling back to simple split")
                return _fallback_simple_split(full_text)
        
        if "fragments" not in fragments_json:
            print("🔴 No 'fragments' key found in response, falling back")
            return _fallback_simple_split(full_text)
        
        fragments = fragments_json["fragments"]
        
        if isinstance(fragments, list):
            # If model returned objects like [{"text": "..."}]
            if fragments and isinstance(fragments[0], dict):
                if "text" in fragments[0]:
                    print("🟡 Converting object format to string array")
                    result = [frag["text"] for frag in fragments if "text" in frag]
                    if result:
                        return result
                print("🔴 Unexpected object format in fragments, falling back")
                return _fallback_simple_split(full_text)
            
            # Normal case: list of strings
            if fragments and isinstance(fragments[0], str):
                clean = [frag.strip() for frag in fragments if frag and isinstance(frag, str)]
                if clean:
                    return clean
                print("🔴 Fragments list is empty after cleaning, falling back")
                return _fallback_simple_split(full_text)
            
            print("🔴 Empty or invalid fragments array, falling back")
            return _fallback_simple_split(full_text)
        
        print("🔴 'fragments' is not an array, falling back")
        return _fallback_simple_split(full_text)
    
    except Exception as e:
        print(f"Error from Gemini in split_text_to_fragments: {e}")
        return _fallback_simple_split(full_text)
