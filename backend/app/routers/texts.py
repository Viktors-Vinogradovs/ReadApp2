from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.text_loader import load_texts
from ..services.textsplitter import split_text_to_fragments

router = APIRouter()

# ----- In-memory storage for uploaded texts (session-only) -----
# Texts are stored only while the server is running
# They are lost when the server restarts
_session_uploads: List[dict] = []


# ----- endpoints -----

@router.get("", response_model=List[dict])
def list_texts(lang: str = "English") -> List[dict]:
    """
    Return all texts (built-in + uploaded) for a given language.
    Shape: [{ name, language, parts }]
    """
    base = load_texts(lang)  # Built-in sample texts
    uploads = [
        x for x in _session_uploads
        if x.get("language", "").lower() == lang.lower()
    ]
    return base + uploads


@router.get("/{name}/parts", response_model=Dict[str, str])
def get_parts(name: str, lang: str = "English") -> Dict[str, str]:
    """
    Return the parts dict for a specific text name.
    """
    texts = list_texts(lang)
    for item in texts:
        if item.get("name") == name:
            return item.get("parts", {})
    raise HTTPException(status_code=404, detail="Text not found")


class UploadTextRequest(BaseModel):
    name: str
    language: str
    text: str
    autoSplit: Optional[bool] = True
    fragmentTargetTokens: Optional[int] = 400


class FragmentPreviewRequest(BaseModel):
    text: str
    targetTokens: Optional[int] = 400


@router.post("/preview")
def preview_fragments(req: FragmentPreviewRequest) -> dict:
    target = req.targetTokens or 400
    pieces = split_text_to_fragments(req.text, target_tokens=target)
    if not pieces:
        # Last-resort: whole text as one fragment if non-empty
        cleaned = req.text.strip()
        if cleaned:
            pieces = [cleaned]
        else:
            raise HTTPException(status_code=400, detail="Empty text")
    return {"fragments": pieces}


@router.post("")
def upload_text(req: UploadTextRequest) -> dict:
    """
    Upload a new text for the current session only.
    Text will be lost when server restarts.
    """
    target_tokens = req.fragmentTargetTokens or 400
    if req.autoSplit:
        pieces = split_text_to_fragments(req.text, target_tokens=target_tokens)
        if not pieces:
            # Last-resort: whole text as one fragment if non-empty
            cleaned = req.text.strip()
            if cleaned:
                pieces = [cleaned]
            else:
                raise HTTPException(status_code=400, detail="Empty text")
        parts = {f"fragment {i+1}": p for i, p in enumerate(pieces)}
    else:
        parts = {"fragment 1": req.text}

    # Store in memory only (session-only storage)
    new_item = {"name": req.name, "language": req.language, "parts": parts}
    _session_uploads.append(new_item)
    
    print(f"📝 Uploaded text '{req.name}' for session (total uploads: {len(_session_uploads)})")
    return {"ok": True, "item": new_item}
