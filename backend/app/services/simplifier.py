from openai import OpenAI
from langchain_core.prompts import PromptTemplate

from backend.app.core.config import settings


_cfg = settings()


_LV_PROMPT = """
    Tu esi radošs un atbalstošs skolotājs, kurš māca 14 gadus vecus bērnus lasīt un saprast stāstus.
    Tavs uzdevums ir pārrakstīt sekojošo tekstu tā, lai tas būtu viegli lasāms un saprotams 14 gadus vecam bērnam, saglabājot:
    – stāsta galvenos pavērsienus un varoņu nodomus,
    – dialogus, kas ataino rīcību un motivāciju,
    – notikumu loģisko secību,
    – precīzus darbības vārdus un to savstarpējo sasaisti,
    – dabisku sarunas plūdumu dialogos.

    Raksti vienmērīgā, paragrāfu formā, nevis punktu veidā. Izmanto:
    – vidēji garus teikumus ar skaidru struktūru,
    – vienkāršus vārdus un konkrētus aprakstus,
    – izvairies no sarežģītiem izteicieniem un metaforām,
    – izlaidi lieko, tomēr neaizmirsti varoņu motivāciju un svarīgākos notikumus.

    Atgriez tikai vienkāršoto tekstu kā saliktu stāstu bez papildu paskaidrojumiem.

    Teksts, kas jāvienkāršo:
    {text}
    """

_EN_PROMPT = """
    You are a creative and supportive teacher guiding 14-year-olds to read and understand stories.
    Your task is to rewrite the following text as a clear, engaging narrative that a 14-year-old can follow, while preserving:
    – the key plot developments and characters' intentions,
    – dialogues that convey action and motivation,
    – the logical sequence of events,
    – precise action verbs,
    – natural conversational flow.

    Write in full paragraphs—avoid lists or bullet points. Use:
    – moderately long sentences with clear structure,
    – simple, concrete words and descriptions,
    – no complex idioms or metaphors,
    – omit extraneous details but keep characters' motivations and essential plot points intact.

    Return only the simplified story text, formatted as a smooth narrative without any additional commentary.

    Text to simplify:
    {text}
    """

_ES_PROMPT = """
    Eres un maestro creativo y solidario que guía a jóvenes de 14 años para leer y comprender historias.
    Tu tarea es reescribir el siguiente texto como una narrativa clara y atractiva que un joven de 14 años pueda seguir, preservando:
    – los desarrollos clave de la trama y las intenciones de los personajes,
    – diálogos que transmitan acción y motivación,
    – la secuencia lógica de eventos,
    – verbos de acción precisos,
    – flujo conversacional natural.

    Escribe en párrafos completos—evita listas o viñetas. Usa:
    – oraciones moderadamente largas con estructura clara,
    – palabras simples y concretas y descripciones,
    – sin modismos complejos o metáforas,
    – omite detalles extraños pero mantén las motivaciones de los personajes y puntos esenciales de la trama intactos.

    Devuelve solo el texto de la historia simplificada, formateado como una narrativa fluida sin comentarios adicionales.

    Texto a simplificar:
    {text}
    """

_RU_PROMPT = """
    Ты творческий и поддерживающий учитель, который помогает 14-летним детям читать и понимать рассказы.
    Твоя задача - переписать следующий текст как ясное, увлекательное повествование, которое может понять 14-летний ребенок, сохраняя:
    – ключевые развития сюжета и намерения персонажей,
    – диалоги, которые передают действие и мотивацию,
    – логическую последовательность событий,
    – точные глаголы действия,
    – естественный разговорный поток.

    Пиши полными абзацами—избегай списков или маркеров. Используй:
    – умеренно длинные предложения с четкой структурой,
    – простые, конкретные слова и описания,
    – никаких сложных идиом или метафор,
    – опускай лишние детали, но сохраняй мотивации персонажей и основные моменты сюжета.

    Верни только упрощенный текст рассказа, отформатированный как плавное повествование без дополнительных комментариев.

    Текст для упрощения:
    {text}
    """

_client = OpenAI(
    api_key=_cfg["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


_LEVEL_HINTS = {
    "gentle": "Focus on clarifying sentences but keep most original vocabulary.",
    "default": "Balance simplicity with original tone.",
    "deep": "Simplify aggressively using very short sentences and everyday vocabulary.",
}


def simplify_text(
    text: str,
    lang: str = "Latvian",
    max_length: int = 15000,
    level: str = "default",
) -> str:
    if len(text) > max_length:
        raise ValueError(f"Text longer than {max_length} characters")

    level_hint = _LEVEL_HINTS.get(level, _LEVEL_HINTS["default"])

    if lang == "English":
        template = _EN_PROMPT
        system_msg = "You are a creative and supportive teacher who teaches children to read with comprehension."
    elif lang == "Spanish":
        template = _ES_PROMPT
        system_msg = "Eres un maestro creativo y solidario que enseña a los niños a leer con comprensión."
    elif lang == "Russian":
        template = _RU_PROMPT
        system_msg = "Ты творческий и поддерживающий учитель, который учит детей читать с пониманием."
    else:
        template = _LV_PROMPT
        system_msg = "Tu esi radošs un atbalstošs skolotājs, kurš māca bērnus lasīt ar izpratni."

    prompt = PromptTemplate(template=template, input_variables=["text"])
    full = prompt.format(text=text) + f"\n\nSimplification aim: {level_hint}"

    resp = _client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": full},
        ],
        stream=False,
    )

    return resp.choices[0].message.content


