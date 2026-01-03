from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.app.core.config import settings
from backend.app.core.llm_factory import get_gemini_llm

_cfg = settings()

# Use lazy-loaded LLM from factory with lower temperature for formatting
def _get_llm():
    return get_gemini_llm(temperature=0.4, top_p=0.7)


def improve_formatting(text: str, language: str = "English") -> str:
    """Ask the LLM to fix spacing, punctuation, sentence casing, and speaker markers."""
    lang = language.lower()
    instructions = {
        "latvian": "Uzlabot teikumu robežas, lielos sākumburtus un dialogu domuzīmes latviešu valodā.",
        "spanish": "Mejora la puntuación y los saltos de línea en español.",
        "russian": "Исправь пунктуацию и абзацы на русском языке.",
    }
    hint = instructions.get(lang, "Improve punctuation, spacing, and paragraphing in English.")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an editor. Clean up formatting, fix missing capital letters, ensure paragraphs break at natural points, "
                "and keep every piece of content from the user's text. Do not summarize; return the original story with better formatting.",
            ),
            ("human", f"{hint}\n\nText:\n{text}"),
        ]
    )

    return (prompt | _get_llm() | StrOutputParser()).invoke({})


