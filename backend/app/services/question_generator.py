import json
import logging
from typing import List, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from backend.app.core.config import settings
from backend.app.core.llm_factory import get_gemini_llm
from backend.app.core.llm_utils import clean_llm_json_response

logger = logging.getLogger(__name__)


_cfg = settings()

# Use lazy-loaded LLM from factory
def _get_llm():
    return get_gemini_llm(temperature=0.7, top_p=0.7)


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

    try:
        response = (prompt | _get_llm() | StrOutputParser()).invoke({})
    except ChatGoogleGenerativeAIError as e:
        error_msg = str(e)
        logger.error(f"Gemini API error: {error_msg}")
        
        # Check for rate limit error
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            raise ValueError(
                "⏳ API rate limit exceeded. Please wait a few moments and try again. "
                "If this persists, consider upgrading your Gemini API plan."
            )
        elif "PERMISSION_DENIED" in error_msg or "API key" in error_msg:
            raise ValueError("🔑 API key error. Please check your Gemini API key configuration.")
        else:
            raise ValueError(f"❌ API error: {error_msg}")
    except Exception as e:
        logger.error(f"Unexpected error during question generation: {e}")
        raise ValueError(f"❌ Failed to generate questions: {str(e)}")

    logger.info("🟡 Raw LLM Response received")
    logger.info(f"🌐 Expected language: {language}")

    # --- Clean potential code fences using centralized utility ---------------
    cleaned = clean_llm_json_response(response)

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
    logger.info(f"✅ Normalized to {len(questions)} questions in {language}")
    return questions


def generate_questions_batch(
    fragments: List[str],
    language: str = "English",
    difficulty: str = "standard",
    text_name: str = ""
) -> Dict:
    """
    Generate questions for multiple fragments in a single API call.
    Provides full story context for better question quality.
    
    Args:
        fragments: List of text fragments
        language: Target language for questions
        difficulty: Question difficulty level
        text_name: Name of the text (for logging)
    
    Returns:
        {
            'questions_by_fragment': {0: ['Q1', 'Q2'], 1: ['Q3', 'Q4'], ...},
            'api_calls': 1
        }
    """
    if not fragments:
        return {'questions_by_fragment': {}, 'api_calls': 0}
    
    logger.info(f"🎯 Batch question generation: {len(fragments)} fragments, language={language}")
    
    # Calculate total size and determine if we can do single batch
    total_chars = sum(len(f) for f in fragments)
    logger.info(f"📊 Total text size: {total_chars} characters")
    
    # Gemini can handle large contexts, but let's be conservative
    # Single batch if < 8000 chars (~2000 tokens)
    if total_chars < 8000:
        logger.info(f"✅ Using SINGLE BATCH mode (1 API call for all {len(fragments)} fragments)")
        return _generate_single_batch(fragments, language, difficulty)
    else:
        # For very large texts, fall back to sequential generation
        logger.warning(f"⚠️ Text too large ({total_chars} chars), using SEQUENTIAL mode ({len(fragments)} API calls)")
        return _generate_sequential(fragments, language, difficulty)


def _generate_single_batch(
    fragments: List[str],
    language: str,
    difficulty: str
) -> Dict:
    """Generate questions for all fragments in ONE API call."""
    
    logger.info("=" * 60)
    logger.info("🔥 STARTING SINGLE BATCH GENERATION (1 API CALL)")
    logger.info("=" * 60)
    
    # Build comprehensive prompt with full context
    hint = _difficulty_hint(difficulty)
    
    # Calculate questions per fragment
    questions_per_fragment = [_calculate_question_count(f) for f in fragments]
    total_questions = sum(questions_per_fragment)
    
    logger.info(f"📝 Requesting {total_questions} total questions across {len(fragments)} fragments")
    
    # Build fragment list for prompt
    fragment_list = "\n\n".join([
        f"FRAGMENT {i}:\n{frag}"
        for i, frag in enumerate(fragments)
    ])
    
    system_msg = (
        f"You are a reading comprehension expert creating questions in {language}.\n\n"
        "TASK: Generate questions for a story divided into fragments.\n"
        "- You will see the ENTIRE story for context\n"
        "- Generate questions for EACH fragment separately\n"
        "- Questions should test comprehension of that specific fragment\n"
        "- But you can reference earlier/later events for better context\n\n"
        f"Generate {total_questions} questions total:\n"
    )
    
    for i, count in enumerate(questions_per_fragment):
        system_msg += f"- Fragment {i}: {count} questions\n"
    
    system_msg += (
        f"\n{hint}\n\n"
        "IMPORTANT: Return ONLY a JSON object in this exact format:\n"
        "{{\n"
        '  "0": ["Question 1 for fragment 0", "Question 2 for fragment 0"],\n'
        '  "1": ["Question 1 for fragment 1", "Question 2 for fragment 1"],\n'
        "  ...\n"
        "}}\n\n"
        f"All questions must be in {language}. No explanations, just the JSON."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", f"FULL STORY:\n\n{fragment_list}\n\nGenerate questions for each fragment:")
    ])
    
    try:
        logger.info("=" * 60)
        logger.info(f"📤 API CALL #1: Sending batch request to Gemini API...")
        logger.info("=" * 60)
        response = (prompt | _get_llm() | StrOutputParser()).invoke({})
        logger.info("=" * 60)
        logger.info(f"📥 API CALL #1 COMPLETE: Received response from Gemini API")
        logger.info("=" * 60)
    except ChatGoogleGenerativeAIError as e:
        error_msg = str(e)
        logger.error(f"Gemini API error in batch generation: {error_msg}")
        
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            raise ValueError(
                "⏳ API rate limit exceeded. Please wait a few moments and try again."
            )
        elif "PERMISSION_DENIED" in error_msg or "API key" in error_msg:
            raise ValueError("🔑 API key error. Please check your Gemini API key configuration.")
        else:
            raise ValueError(f"❌ API error: {error_msg}")
    except Exception as e:
        logger.error(f"Unexpected error during batch question generation: {e}")
        raise ValueError(f"❌ Failed to generate questions: {str(e)}")
    
    logger.info("🟡 Received batch response from LLM")
    
    # Parse response
    cleaned = clean_llm_json_response(response)
    
    logger.info(f"🔍 Cleaned response (first 500 chars): {cleaned[:500]}")
    
    try:
        parsed = json.loads(cleaned)
        logger.info("✅ JSON parsing successful")
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error: {e}")
        logger.error(f"📄 Full cleaned response:\n{cleaned}")
        
        # Try quote fix
        try:
            logger.info("🔄 Attempting quote fix...")
            cleaned_fixed = cleaned.replace("'", '"')
            parsed = json.loads(cleaned_fixed)
            logger.info("✅ JSON parsing successful after quote fix")
        except json.JSONDecodeError as e2:
            logger.error(f"❌ JSON parsing failed even after quote fix: {e2}")
            logger.error(f"📄 Attempted to parse:\n{cleaned_fixed}")
            
            # DON'T fall back to sequential - raise error instead!
            raise ValueError(
                f"Failed to parse LLM response as JSON. "
                f"This is likely a prompt/format issue, not a rate limit. "
                f"Response preview: {cleaned[:200]}..."
            )
    
    # Convert string keys to integers and validate
    questions_by_fragment = {}
    for key, value in parsed.items():
        try:
            idx = int(key)
            if isinstance(value, list) and all(isinstance(q, str) for q in value):
                questions_by_fragment[idx] = value
            else:
                logger.warning(f"Invalid format for fragment {idx}, skipping")
        except (ValueError, TypeError):
            logger.warning(f"Invalid key '{key}', skipping")
    
    logger.info(f"✅ Successfully generated questions for {len(questions_by_fragment)} fragments in 1 API call")
    
    return {
        'questions_by_fragment': questions_by_fragment,
        'api_calls': 1
    }


def _generate_sequential(
    fragments: List[str],
    language: str,
    difficulty: str
) -> Dict:
    """Fallback: Generate questions fragment-by-fragment."""
    
    logger.warning("=" * 60)
    logger.warning(f"⚠️ USING SEQUENTIAL MODE: {len(fragments)} SEPARATE API CALLS")
    logger.warning("=" * 60)
    
    questions_by_fragment = {}
    api_calls = 0
    
    for i, fragment in enumerate(fragments):
        try:
            logger.warning("=" * 60)
            logger.warning(f"📤 API CALL #{i+2}: Generating questions for fragment {i}...")
            logger.warning(f"⚠️ THIS IS AN ADDITIONAL API CALL (not part of batch)")
            logger.warning("=" * 60)
            questions = generate_questions(fragment, [], language, difficulty)
            questions_by_fragment[i] = questions
            api_calls += 1
            logger.info(f"✅ Fragment {i} complete")
        except Exception as e:
            logger.error(f"❌ Failed to generate questions for fragment {i}: {e}")
            questions_by_fragment[i] = []
    
    logger.warning(f"⚠️ Sequential generation complete: {api_calls} TOTAL API CALLS")
    
    return {
        'questions_by_fragment': questions_by_fragment,
        'api_calls': api_calls
    }
