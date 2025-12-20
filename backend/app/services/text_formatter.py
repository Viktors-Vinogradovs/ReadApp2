from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.core.config import settings

_cfg = settings()

_formatter = ChatGoogleGenerativeAI(
    model=_cfg["GEMINI_QUESTION_MODEL"],
    api_key=_cfg["GEMINI_API_KEY"],
    temperature=0.4,
    top_p=0.7,
)


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

    return (prompt | _formatter | StrOutputParser()).invoke({})


