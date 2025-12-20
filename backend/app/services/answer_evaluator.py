import hashlib
import json
import re
import time
from collections import defaultdict
from uuid import uuid4

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.core.config import settings


_cfg = settings()

llm_evaluation = ChatGoogleGenerativeAI(
    model=_cfg["GEMINI_QUESTION_MODEL"],
    api_key=_cfg["GEMINI_API_KEY"],
    temperature=0.7,
    top_p=0.7,
)


class TokenBucketRateLimiter:
    def __init__(self, capacity: int = 8, refill_rate: float = 0.15):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = defaultdict(
            lambda: {
                "tokens": capacity,
                "last_refill": time.time(),
            }
        )

    def is_allowed(self, user_id: str) -> tuple[bool, float]:
        now = time.time()
        bucket = self.buckets[user_id]

        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * self.refill_rate
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, 0

        wait_time = (1 - bucket["tokens"]) / self.refill_rate
        return False, wait_time


_rate_limiter = TokenBucketRateLimiter(capacity=8, refill_rate=0.15)
_DEFAULT_USER_ID = hashlib.md5(str(uuid4()).encode()).hexdigest()[:12]

STRICTNESS_HINTS = {
    1: "Be encouraging and lenient. Accept answers that capture the main idea even if details differ.",
    2: "Be fair and balanced. Minor paraphrasing is acceptable, but the answer must mention the key idea.",
    3: "Be strict. The answer must closely match the referenced text and include precise details.",
}


def get_user_session_id(user_id: str | None = None) -> str:
    if user_id and isinstance(user_id, str) and user_id.strip():
        return user_id.strip()
    return _DEFAULT_USER_ID


def evaluate_answer(
    fragment,
    question,
    user_answer,
    language="English",
    user_id: str | None = None,
    strictness: int = 2,
):
    print(f"🔍 Answer evaluation for language: {language}")

    uid = get_user_session_id(user_id)
    allowed, wait_time = _rate_limiter.is_allowed(uid)

    if not allowed:
        if language.lower() == "latvian":
            feedback = "Lūdzu, uzgaidiet brīdi pirms nākamās atbildes."
        elif language.lower() == "spanish":
            feedback = "Por favor, espera un momento antes de la siguiente respuesta."
        elif language.lower() == "russian":
            feedback = "Пожалуйста, подождите немного перед следующим ответом."
        else:
            feedback = "Please wait a moment before your next answer."

        return {
            "feedback": feedback,
            "correct_snippet": "",
            "correct": False,
            "rate_limited": True,
            "wait_time": wait_time,
        }

    level_hint = STRICTNESS_HINTS.get(strictness, STRICTNESS_HINTS[2])

    if language.lower() == "latvian":
        system_msg = (
            "Tu esi skolotājs, kas īsi vērtē bērna atbildi. "
            "Atbildi TIKAI kā JSON objektu. Nekādus ```json vai komentārus neliec. "
            "Bez komentāriem vai papildu teksta. "
            "JSON struktūra: {{\"feedback\":\"...\",\"correct_snippet\":\"...\",\"correct\":true/false}}. "
            "• 'feedback' - īss teikums par atbildi. "
            "• 'correct_snippet' - ĪSS citāts no Teksta (maksimums 20 vārdi), kas pierāda pareizo atbildi. "
            "  Izvēlies mazāko iespējamo frāzi, kas satur galveno informāciju, nevis veselu rindkopu. "
            "• 'correct' - true, ja pareizi, false, ja nepareizi."
            f" {level_hint}"
        )
    elif language.lower() == "spanish":
        system_msg = (
            "Eres un maestro que evalúa respuestas de niños. "
            "Responde SOLO como un objeto JSON. No agregues ```json o comentarios. "
            "Sin comentarios o texto adicional. "
            "Formato JSON: {{\"feedback\":\"...\",\"correct_snippet\":\"...\",\"correct\":true/false}}. "
            "• 'feedback' - oración breve sobre la respuesta. "
            "• 'correct_snippet' - una cita CORTA del Texto (máximo 20 palabras) que prueba la respuesta correcta. "
            "  Elige la frase más pequeña posible que contenga la información clave, no un párrafo completo. "
            "• 'correct' - true si es correcto, false si no. "
            "Sé flexible con ortografía y tildes, pero verifica que la idea principal sea correcta."
            f" {level_hint}"
        )
    elif language.lower() == "russian":
        system_msg = (
            "Ты учитель, который оценивает ответы детей. "
            "Отвечай ТОЛЬКО в виде JSON объекта. Не добавляй ```json или комментарии. "
            "Без комментариев или дополнительного текста. "
            "Формат JSON: {{\"feedback\":\"...\",\"correct_snippet\":\"...\",\"correct\":true/false}}. "
            "• 'feedback' - краткое предложение об ответе. "
            "• 'correct_snippet' - КОРОТКАЯ цитата из Текста (максимум 20 слов), доказывающая правильный ответ. "
            "  Выбери минимально возможную фразу, содержащую ключевую информацию, а не целый абзац. "
            "• 'correct' - true если правильно, false если нет. "
            "Будь гибким с орфографией и буквой ё, но проверяй, что основная идея правильна."
            f" {level_hint}"
        )
    else:
        system_msg = (
            "You are a teacher evaluating a child's answer. "
            "Respond ONLY as a JSON object. No ```json or comments. "
            "No additional commentary or text. "
            "JSON format: {{\"feedback\":\"...\",\"correct_snippet\":\"...\",\"correct\":true/false}}. "
            "• 'feedback' - a short sentence about the answer. "
            "• 'correct_snippet' - a SHORT quote from the Text (max 20 words) that proves the correct answer. "
            "  Choose the smallest possible phrase that contains the key information, not a whole paragraph. "
            "• 'correct' - true if correct, false otherwise."
            f" {level_hint}"
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", f"Text:\n{fragment}\n\nQuestion:\n{question}\n\nChild's answer:\n{user_answer}"),
    ])

    response = (prompt | llm_evaluation | StrOutputParser()).invoke({})

    print("🟡 Raw LLM Response:", response)
    print(f"🌐 Expected language: {language}")

    try:
        if response.strip().startswith("```json"):
            response = response.strip().removeprefix("```json").removesuffix("```").strip()
        elif response.strip().startswith("```"):
            response = response.strip().removeprefix("```").removesuffix("```").strip()

        result_dict = json.loads(response)
        print(f"✅ Evaluation completed for {language}")

        result_dict.setdefault("feedback", "")
        result_dict.setdefault("correct_snippet", "")
        if "correct" in result_dict:
            result_dict["correct"] = str(result_dict["correct"]).lower() == "true"
        else:
            result_dict["correct"] = False

        # Post-process correct_snippet to enforce length limits
        snippet = result_dict.get("correct_snippet", "") or ""
        snippet = snippet.strip()
        
        if snippet:
            words = snippet.split()
            if len(words) > 25 or len(snippet) > 250:
                # Take only first sentence or first ~25 words
                # 1) cut at first sentence end
                parts = re.split(r'([.!?])', snippet, maxsplit=1)
                if len(parts) >= 2:
                    snippet = (parts[0] + parts[1]).strip()
                # 2) if still too long, limit to first 25 words
                words = snippet.split()
                if len(words) > 25:
                    snippet = " ".join(words[:25])
                result_dict["correct_snippet"] = snippet

        result_dict["rate_limited"] = False
        result_dict["wait_time"] = 0

        return result_dict

    except json.JSONDecodeError as e:
        print(f"🔴 JSON decode error: {e}")
        print(f"🔴 Response was: {response}")

        if language.lower() == "latvian":
            feedback = "Kļūda apstrādājot atbildi. Lūdzu, mēģiniet vēlreiz."
        elif language.lower() == "spanish":
            feedback = "Error procesando la respuesta. Por favor, inténtalo de nuevo."
        elif language.lower() == "russian":
            feedback = "Ошибка обработки ответа. Пожалуйста, попробуйте снова."
        else:
            feedback = "Error processing answer. Please try again."

        return {
            "feedback": feedback,
            "correct_snippet": "",
            "correct": False,
            "rate_limited": False,
            "wait_time": 0,
            "error": str(e),
        }
    except Exception as e:
        print(f"🔴 Unexpected error: {e}")

        if language.lower() == "latvian":
            feedback = "Negaidīta kļūda. Lūdzu, mēģiniet vēlreiz."
        elif language.lower() == "spanish":
            feedback = "Error inesperado. Por favor, inténtalo de nuevo."
        elif language.lower() == "russian":
            feedback = "Неожиданная ошибка. Пожалуйста, попробуйте снова."
        else:
            feedback = "Unexpected error. Please try again."

        return {
            "feedback": feedback,
            "correct_snippet": "",
            "correct": False,
            "rate_limited": False,
            "wait_time": 0,
            "error": str(e),
        }


