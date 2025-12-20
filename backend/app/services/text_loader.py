import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
TEXTS_FILE = DATA_DIR / "texts.json"


def load_texts(language: str = "English"):
    if not TEXTS_FILE.exists():
        return []

    with TEXTS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # Handle both old format {"texts": [...]} and new format [...]
    texts_list = data if isinstance(data, list) else data.get("texts", [])

    return [
        {
            "name": t["name"],
            "language": t.get("language", language),
            "parts": t["parts"],
        }
        for t in texts_list
        if t.get("language", "").lower() == language.lower()
    ]


def get_fragment(text_name: str, part_name: str, language: str = "English") -> str:
    texts = load_texts(language)
    for text in texts:
        if text["name"] == text_name:
            return text.get("parts", {}).get(part_name, "")
    return ""


