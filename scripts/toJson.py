"""Utility script to add texts to JSON library.

This script is used to process and add new texts to the application's
data/texts.json file with automatic text splitting.

Usage:
    python scripts/toJson.py
"""

import json
import os
import sys
from pathlib import Path

# Add backend to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.textsplitter import split_text_to_fragments


def add_text_to_json(file_path, text, language, title):
    """
    Add a text to the JSON library with automatic fragmentation.
    
    Args:
        file_path: Path to texts.json file
        text: Full text content
        language: Language code (English, Latvian, Spanish, Russian)
        title: Display title for the text
    """
    fragments = split_text_to_fragments(text)
    if not fragments:
        print("❌ Failed to split text into fragments.")
        return

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"texts": []}

    # Avoid duplicate titles for the same language
    for text_entry in data["texts"]:
        if text_entry["language"] == language and text_entry["name"].strip().lower() == title.strip().lower():
            print(f"⚠️ Text with title '{title}' already exists in {language}.")
            return

    # Create parts dictionary with preserved formatting
    # Remove soft hyphens only
    parts = {}
    for i, fragment in enumerate(fragments):
        clean_fragment = fragment.replace("\u00AD", "") if fragment else ""
        parts[f"fragment {i + 1}"] = clean_fragment

    entry = {
        "language": language,
        "name": title.strip(),
        "source": "upload",
        "parts": parts
    }

    data["texts"].append(entry)

    # Use indent=4 to make the JSON more readable
    # ensure_ascii=False to properly handle non-ASCII characters
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Added '{title}' to {file_path}")


# === CLI Test ===
if __name__ == "__main__":
    # Test with sample text
    test_file = "Pasakas/Горячий_камень.txt"

    # If file doesn't exist, use a simple test
    if os.path.exists(test_file):
        with open(test_file, "r", encoding="utf-8") as f:
            sample = f.read()
    else:
        sample = """
        Viņš nebija ne liels, ne mazs, ne resns, ne tievs, un par sevi viņš nekā jēdzīga pastāstīt nevarēja, jo, kā jau īstam Murmulītim pienākas, viņš murmulēja gan šo, gan to, bet galu galā nepateica neko.

        Murmulītis gulšņāja uz diža, nosūnojuša akmens kalna nogāzē un, savā nodabā murmulēdams, noskatījās elfu dejās netālajā pļaviņā.
        """

    # Remove soft hyphens but keep all other formatting
    sample = sample.replace("\u00AD", "")
    add_text_to_json("data/texts.json", sample, "Russian", "Горячий камень")

