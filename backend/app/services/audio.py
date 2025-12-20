import re
import time
from pathlib import Path

import requests
from gradio_client import Client

from backend.app.core.config import settings

_cfg = settings()
HF_API_TOKEN = _cfg["HF_API_TOKEN"]

TTS_CONFIG = {
    "English": {
        "service": "multilingual_tts",
        "space_name": "MohamedRashad/Multilingual-TTS",
        "api_name": "/text_to_speech_edge",
        "language_code": "English",
    },
    "Latvian": {
        "service": "spaces_api",
        "space_name": "RaivisDejus/Latvian-Piper-TTS",
        "api_name": "/synthesize_speech",
    },
    "Spanish": {
        "service": "multilingual_tts",
        "space_name": "MohamedRashad/Multilingual-TTS",
        "api_name": "/text_to_speech_edge",
        "language_code": "Spanish",
    },
    "Russian": {
        "service": "multilingual_tts",
        "space_name": "MohamedRashad/Multilingual-TTS",
        "api_name": "/text_to_speech_edge",
        "language_code": "Russian",
    },
}


def clean_text_for_tts(text: str) -> str:
    """
    Clean text for TTS by removing markdown, HTML, and normalizing punctuation.
    Based on working Streamlit implementation.
    """
    # Strip markdown bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('„', '"').replace('‚', '"')  # German-style quotes
    
    # Normalize dashes
    text = text.replace('—', '-').replace('–', '-')
    
    # Normalize ellipsis
    text = text.replace('…', '...')
    
    # Fix common English abbreviations that TTS might struggle with
    text = re.sub(r'\bDr\.', 'Doctor', text)
    text = re.sub(r'\bMr\.', 'Mister', text)
    text = re.sub(r'\bMrs\.', 'Missus', text)
    text = re.sub(r'\bMs\.', 'Miss', text)
    text = re.sub(r'\betc\.', 'etcetera', text)
    text = re.sub(r'\bi\.e\.', 'that is', text)
    text = re.sub(r'\be\.g\.', 'for example', text)
    
    # Fix common Russian abbreviations
    text = re.sub(r'\bт\.д\.', 'так далее', text)
    text = re.sub(r'\bт\.е\.', 'то есть', text)
    text = re.sub(r'\bт\.к\.', 'так как', text)
    text = re.sub(r'\bт\.п\.', 'тому подобное', text)
    text = re.sub(r'\bи т\.д\.', 'и так далее', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Add proper punctuation if missing
    if text and text[-1] not in '.!?':
        text += '.'
    
    print(f"📏 Text length for TTS: {len(text)} characters")
    return text


def process_audio_result(result) -> bytes | None:
    """
    Process various audio result formats from Gradio clients.
    Returns audio bytes or None.
    """
    try:
        # If it's already bytes
        if isinstance(result, bytes):
            return result
        
        # If it's a string (file path)
        if isinstance(result, str):
            path = Path(result)
            if path.exists():
                return path.read_bytes()
            print(f"⚠️ Audio file path does not exist: {result}")
            return None
        
        # If it's a tuple, first element might be the file path
        if isinstance(result, tuple) and len(result) > 0:
            first = result[0]
            if isinstance(first, str):
                path = Path(first)
                if path.exists():
                    return path.read_bytes()
            elif isinstance(first, bytes):
                return first
        
        print(f"⚠️ Unexpected audio result type: {type(result)}")
        return None
    except Exception as e:
        print(f"❌ Error processing audio result: {e}")
        return None


def generate_audio_multilingual_tts(text: str, language_code: str) -> bytes | None:
    """
    Generate audio using MohamedRashad/Multilingual-TTS space.
    Based on working Streamlit implementation.
    """
    try:
        client = Client("MohamedRashad/Multilingual-TTS")
        
        # Default speakers for each language
        default_speakers = {
            "English": "Jenny",
            "Spanish": "Elena",
            "Russian": "Svetlana",
        }
        speaker = None
        
        # Try to get available speakers for the language
        try:
            speakers_result = client.predict(
                language=language_code,
                api_name="/get_speakers"
            )
            print(f"🔍 Raw speakers result for {language_code}: {speakers_result}")
            
            # Parse the speaker result - it returns a complex object
            if isinstance(speakers_result, dict):
                # Extract choices from the response
                choices = speakers_result.get('choices', [])
                if choices and len(choices) > 0:
                    # Each choice is a list like ['Elena', 'Elena'], take the first element
                    speaker = choices[0][0] if isinstance(choices[0], list) else choices[0]
                elif 'value' in speakers_result:
                    speaker = speakers_result['value']
            elif isinstance(speakers_result, list) and len(speakers_result) > 0:
                # If it's a simple list, take the first speaker
                speaker = speakers_result[0]
            
            print(f"✅ Selected speaker for {language_code}: {speaker}")
        except Exception as e:
            print(f"⚠️ Could not get speakers for {language_code}, using default: {e}")
        
        # Ensure we have a speaker - use default if needed
        if not speaker:
            speaker = default_speakers.get(language_code, "Jenny")
            print(f"📌 Using default speaker: {speaker}")
        
        print(f"🎤 Final speaker selection: {speaker} for {language_code}")
        
        # Generate the TTS audio
        result = client.predict(
            text=text,
            language_code=language_code,
            speaker=speaker,
            tashkeel_checkbox=False,  # Arabic text processing, not needed
            api_name="/text_to_speech_edge"
        )
        
        print(f"📦 TTS result type: {type(result)}, content preview: {str(result)[:100]}")
        
        # The result should be a tuple with [audio_text, audio_file_path]
        if isinstance(result, tuple) and len(result) >= 2:
            audio_file_path = result[1]  # Second element is the audio file
            if isinstance(audio_file_path, str) and audio_file_path:
                try:
                    path = Path(audio_file_path)
                    if path.exists():
                        audio_data = path.read_bytes()
                        print(f"✅ Successfully read audio file: {len(audio_data)} bytes")
                        return audio_data
                    else:
                        print(f"❌ Generated audio file not found: {audio_file_path}")
                        return None
                except Exception as e:
                    print(f"❌ Error reading audio file: {e}")
                    return None
            else:
                print(f"❌ Invalid audio file path: {audio_file_path}")
                return None
        elif isinstance(result, str):
            # Sometimes the API might return just the file path
            try:
                path = Path(result)
                if path.exists():
                    audio_data = path.read_bytes()
                    print(f"✅ Successfully read audio file from string path: {len(audio_data)} bytes")
                    return audio_data
                else:
                    print(f"❌ Generated audio file not found: {result}")
                    return None
            except Exception as e:
                print(f"❌ Error reading audio file: {e}")
                return None
        else:
            print(f"❌ Unexpected result format from Multilingual TTS: {type(result)} - {result}")
            return None
    
    except Exception as e:
        print(f"❌ Detailed Multilingual TTS error for {language_code}: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_audio_spaces_latvian(text: str) -> bytes | None:
    """
    Generate audio using RaivisDejus/Latvian-Piper-TTS space.
    """
    try:
        client = Client("RaivisDejus/Latvian-Piper-TTS")
        
        result = client.predict(
            text,
            0.1,  # sentence_silence
            1.0,  # length_scale
            api_name="/synthesize_speech"
        )
        
        return process_audio_result(result)
    
    except Exception as e:
        print(f"❌ Latvian TTS error: {e}")
        return None


def _hf_router_tts(text: str, model_id: str) -> bytes | None:
    """
    Fallback TTS using HuggingFace router API.
    """
    url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(url, headers=headers, json={"inputs": text}, timeout=120)
        
        if resp.status_code == 200:
            return resp.content
        
        # Retry once on 503 (model loading)
        if resp.status_code == 503:
            print(f"⏳ Model loading, waiting 15s...")
            time.sleep(15)
            resp = requests.post(url, headers=headers, json={"inputs": text}, timeout=120)
            if resp.status_code == 200:
                return resp.content
        
        print(f"❌ TTS HF router error {resp.status_code}: {resp.text}")
        return None
    
    except Exception as e:
        print(f"❌ HF router TTS exception: {e}")
        return None


def generate_audio_hf_api(text: str, language: str = "English") -> bytes | None:
    """
    Generate audio using appropriate HuggingFace API based on language.
    """
    if not text.strip():
        return None
    
    cfg = TTS_CONFIG.get(language, TTS_CONFIG["English"])
    
    if cfg["service"] == "multilingual_tts":
        return generate_audio_multilingual_tts(text, cfg["language_code"])
    elif language == "Latvian":
        return generate_audio_spaces_latvian(text)
    else:
        print(f"⚠️ Unsupported language in TTS_CONFIG: {language}")
        return None


def synthesize_audio(text: str, language: str = "English") -> bytes:
    """
    Clean text and generate TTS audio bytes for the given language.
    Raise ValueError with a helpful message if generation fails.
    """
    clean = clean_text_for_tts(text)
    audio = generate_audio_hf_api(clean, language)
    
    # Fallbacks via HF router for all languages if primary fails
    if audio is None:
        print(f"🔄 Primary TTS failed for {language}, trying HF router fallback...")
        
        fallback_models = {
            "English": "facebook/mms-tts-eng",
            "Russian": "facebook/mms-tts-rus",
            "Spanish": "facebook/mms-tts-spa",
            "Latvian": "facebook/mms-tts-lav",
        }
        
        model = fallback_models.get(language)
        if model:
            audio = _hf_router_tts(clean, model)
    
    if not audio:
        raise ValueError(f"TTS generation failed for language={language}")
    
    return audio
