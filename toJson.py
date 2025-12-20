import json
import os
import re

from backend.app.services.textsplitter import split_text_to_fragments


def add_text_to_json(file_path, text, language, title):
    fragments = split_text_to_fragments(text)
    if not fragments:
        print("Failed to split text into fragments.")
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
    # MINIMAL FIX: Just remove soft hyphens like in your original approach
    parts = {}
    for i, fragment in enumerate(fragments):
        # Keep your original approach - just remove soft hyphens
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


# === Optional CLI Test - KEEP YOUR ORIGINAL APPROACH ===
if __name__ == "__main__":
    # Test with your original file path structure
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

    # Remove soft hyphens but keep all other formatting - YOUR ORIGINAL APPROACH
    sample = sample.replace("\u00AD", "")
    add_text_to_json("texts.json", sample, "Russian", "Горячий камень")