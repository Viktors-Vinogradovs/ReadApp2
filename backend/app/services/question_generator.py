import json

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.core.config import settings


_cfg = settings()

llm_question = ChatGoogleGenerativeAI(
    model=_cfg["GEMINI_QUESTION_MODEL"],
    api_key=_cfg["GEMINI_API_KEY"],
    temperature=0.7,
    top_p=0.7,
)


def _difficulty_hint(difficulty: str) -> str:
    diff = (difficulty or "standard").lower()
    if diff in {"easy", "simpler"}:
        return (
            "\nMake questions VERY simple (max 12 words) and focus on literal recall. "
            "Use vocabulary suitable for early readers."
        )
    if diff in {"challenge", "hard"}:
        return (
            "\nAsk deeper inferential questions that require explaining reasons, feelings, or lessons."
        )
    return ""


def _calculate_question_count(fragment: str) -> int:
    """Calculate number of questions based on fragment length."""
    char_count = len(fragment.strip())
    
    if char_count < 300:
        return 2  # Short fragment: 2 questions
    elif char_count < 600:
        return 3  # Medium fragment: 3 questions
    elif char_count < 1000:
        return 4  # Long fragment: 4 questions
    else:
        return 5  # Very long fragment: 5 questions


def _build_system_message(language: str, previous_questions, difficulty: str, num_questions: int = 3):
    lang = language.lower()
    hint = _difficulty_hint(difficulty)
    
    # Translate question count to words
    count_words = {
        2: {"en": "TWO", "lv": "DIVUS", "es": "DOS", "ru": "ДВА"},
        3: {"en": "THREE", "lv": "TRIS", "es": "TRES", "ru": "ТРИ"},
        4: {"en": "FOUR", "lv": "ČETRUS", "es": "CUATRO", "ru": "ЧЕТЫРЕ"},
        5: {"en": "FIVE", "lv": "PIECUS", "es": "CINCO", "ru": "ПЯТЬ"},
    }
    
    # We always force:
    # - EXACTLY a JSON array
    # - elements are plain strings (questions only)
    # - no answers, no objects, no markdown
    if lang == "latvian":
        count_word = count_words.get(num_questions, {}).get("lv", "TRIS")
        return (
            f"Tu esi draudzīgs skolotājs, kurš ģenerē {count_word} īsus jautājumus bērniem.\n"
            f"Tev JĀATBILST ar TIEŠI derīgu JSON masīvu no {num_questions} virkņu elementiem.\n"
            "KATRS elements ir TIKAI jautājuma teksts.\n"
            "NELIEC atbildes.\n"
            "NELIETO objektus ar atslēgām, piemēram, 'question' vai 'answer'.\n"
            "NELIEC papildu tekstu, komentārus vai markdown (` ``` `).\n"
            "Izmanto derīgu JSON ar dubultajiem pēdiņām ap katru virkni.\n\n"
            "Pareizs izvades piemērs:\n"
            "[\n"
            "  \"Kas ir galvenā šī stāsta doma?\",\n"
            "  \"Kāpēc varonis jutās skumjš?\",\n"
            "  \"Kādu mācību mēs varam gūt no šī teksta?\"\n"
            "]\n\n"
            "Jautājumi jāuzdod TIKAI latviešu valodā.\n"
            f"Pārliecinies, ka jautājumi nav pārāk līdzīgi iepriekšējiem jautājumiem {previous_questions}."
            f"{hint}"
        )

    if lang == "spanish":
        count_word = count_words.get(num_questions, {}).get("es", "TRES")
        return (
            f"Eres un maestro amigable que genera {count_word} preguntas cortas para niños.\n"
            f"DEBES responder con EXACTAMENTE un array JSON válido de {num_questions} cadenas.\n"
            "Cada elemento DEBE ser SOLO el texto de la pregunta.\n"
            "NO incluyas respuestas.\n"
            "NO uses objetos con claves como 'question' o 'answer'.\n"
            "NO añadas texto adicional, comentarios ni markdown (` ``` `).\n"
            "Usa JSON válido con comillas dobles alrededor de cada cadena.\n\n"
            "Ejemplo de salida correcta:\n"
            "[\n"
            "  \"¿Cuál es la idea principal del texto?\",\n"
            "  \"¿Por qué el personaje se siente triste?\",\n"
            "  \"¿Qué lección podemos aprender de esta historia?\"\n"
            "]\n\n"
            "Genera las preguntas SOLO en español.\n"
            f"Asegúrate de que las preguntas no sean demasiado similares a las preguntas anteriores {previous_questions}."
            f"{hint}"
        )

    if lang == "russian":
        count_word = count_words.get(num_questions, {}).get("ru", "ТРИ")
        return (
            f"Ты дружелюбный учитель, который генерирует {count_word} коротких вопроса для детей.\n"
            f"ТЫ ДОЛЖЕН ответить СТРОГО в виде корректного JSON-массива из {num_questions} строк.\n"
            "Каждый элемент ДОЛЖЕН быть ТОЛЬКО текстом вопроса.\n"
            "НЕ добавляй ответы.\n"
            "НЕ используй объекты с ключами вроде 'question' или 'answer'.\n"
            "НЕ добавляй лишний текст, комментарии или markdown (` ``` `).\n"
            "Используй корректный JSON с двойными кавычками вокруг всех строк.\n\n"
            "Пример правильного вывода:\n"
            "[\n"
            "  \"Какова главная мысль этого текста?\",\n"
            "  \"Почему герой чувствовал себя грустным?\",\n"
            "  \"Какой урок мы можем вынести из этой истории?\"\n"
            "]\n\n"
            "Генерируй вопросы ТОЛЬКО на русском языке.\n"
            f"Убедись, что вопросы не слишком похожи на предыдущие вопросы {previous_questions}."
            f"{hint}"
        )

    # Default: English
    count_word = count_words.get(num_questions, {}).get("en", "THREE")
    return (
        f"You are a friendly teacher generating {count_word} short questions for children.\n"
        f"You MUST respond with EXACTLY a valid JSON array of {num_questions} strings.\n"
        "Each element MUST be ONLY the question text.\n"
        "Do NOT include answers.\n"
        "Do NOT include objects with keys like 'question' or 'answer'.\n"
        "Do NOT include any extra text, comments, or markdown fences (` ``` `).\n"
        "Use valid JSON with double quotes around all strings.\n\n"
        "Correct output example:\n"
        "[\n"
        "  \"What is the main idea of the story?\",\n"
        "  \"Why did the hero feel sad?\",\n"
        "  \"What lesson can we learn from this text?\"\n"
        "]\n\n"
        "Generate questions ONLY in English.\n"
        f"Make sure the questions are not too similar to previous questions {previous_questions}."
        f"{hint}"
    )


def generate_questions(fragment, previous_questions=None, language="English", difficulty: str = "standard"):
    if previous_questions is None:
        previous_questions = []

    print(f"🔍 Question generation for language: {language}")
    
    # Calculate number of questions based on fragment length
    num_questions = _calculate_question_count(fragment)
    print(f"📊 Fragment length: {len(fragment)} chars → {num_questions} questions")

    system_msg = _build_system_message(language, previous_questions, difficulty, num_questions)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_msg),
            ("human", f"Text:\n{fragment}"),
        ]
    )

    response = (prompt | llm_question | StrOutputParser()).invoke({})

    print("🟡 Raw LLM Response:", response)
    print(f"🌐 Expected language: {language}")

    # --- Clean potential code fences -----------------------------------------
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").removesuffix("```").strip()

    def normalize_questions(parsed):
        """
        Normalize LLM output to a list[str].

        Handles:
        - ["q1", "q2", "q3"]
        - [{"question": "...", "answer": "..."}, ...]
        - {"question": "...", "answer": "..."}
        - fallback: stringify structured data
        """
        # Ideal case: list of strings
        if isinstance(parsed, list):
            if all(isinstance(q, str) for q in parsed):
                return parsed

            # List of dicts → use "question" key
            if all(isinstance(q, dict) for q in parsed):
                qs = []
                for q in parsed:
                    if "question" in q and isinstance(q["question"], str):
                        qs.append(q["question"])
                if qs:
                    return qs

        # Single dict with "question"
        if isinstance(parsed, dict):
            if "question" in parsed and isinstance(parsed["question"], str):
                return [parsed["question"]]

        # Fallbacks
        if isinstance(parsed, (list, dict)):
            return [json.dumps(parsed, ensure_ascii=False)]
        if isinstance(parsed, str):
            return [parsed]

        return []

    # --- Parse JSON safely ----------------------------------------------------
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        print("🔴 JSON decode error. Initial response was:", cleaned)
        # Last-chance: naive single-quote → double-quote fix
        try:
            cleaned_fixed = cleaned.replace("'", '"')
            parsed = json.loads(cleaned_fixed)
        except json.JSONDecodeError:
            print("🔴 Second JSON decode error after quote fix.")
            return []

    questions = normalize_questions(parsed)
    print(f"✅ Normalized to {len(questions)} questions in {language}")
    return questions
