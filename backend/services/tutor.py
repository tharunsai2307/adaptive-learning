"""AI Tutor service — Google Gemini for chat/quiz generation, with an offline fallback.

The Gemini call is best-effort: if there is no API key, no network, or the API
returns an error, the tutor answers from the seeded topic content instead of
letting the exception bubble up as a 500.
"""

import json
import logging

import httpx

from ..config import settings

log = logging.getLogger(__name__)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

TIMEOUT_SECONDS = 45

STYLE_HINTS = {
    "fast": "Use advanced language, assume strong prior knowledge, be concise and go straight to the depth.",
    "normal": "Use clear language with moderate detail and worked examples.",
    "slow": "Use very simple language, break concepts into small steps, and give basic everyday examples.",
}

STYLE_LABELS = {"fast": "Accelerated", "normal": "Standard", "slow": "Supportive"}


def is_gemini_configured() -> bool:
    return bool(settings.GEMINI_API_KEY)


async def _call_gemini(prompt: str) -> str | None:
    """Send a prompt to Gemini. Returns None if it cannot be reached."""
    if not settings.GEMINI_API_KEY:
        log.info("GEMINI_API_KEY not set — using the offline tutor.")
        return None

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            resp = await client.post(
                GEMINI_URL,
                params={"key": settings.GEMINI_API_KEY},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 2048,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, OSError, ValueError) as exc:
        log.warning("Gemini request failed (%s) — falling back to the offline tutor.", exc)
        return None

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        log.warning("Unexpected Gemini response shape — falling back to the offline tutor.")
        return None


# ── Public API ─────────────────────────────────────────────────────


async def ask_tutor(
    topic_name: str,
    question: str,
    teaching_style: str = "normal",
    topic_content: dict | None = None,
) -> tuple[str, str]:
    """
    Ask the AI tutor a question about the current topic.

    Returns ``(answer, source)`` where source is ``"gemini"`` when the live
    model answered and ``"offline"`` when the grounded fallback was used.
    """
    style_hint = STYLE_HINTS.get(teaching_style, STYLE_HINTS["normal"])

    prompt = (
        f"You are an AI tutor for the topic: '{topic_name}'.\n"
        f"Teaching style: {style_hint}\n\n"
        f"Student question: {question}\n\n"
        "Provide a clear, helpful, and encouraging answer. "
        "Use examples where appropriate."
    )
    answer = await _call_gemini(prompt)
    if answer and answer.strip():
        return answer.strip(), "gemini"
    return (
        _offline_answer(topic_name, question, teaching_style, topic_content or {}),
        "offline",
    )


def _offline_answer(
    topic_name: str, question: str, style: str, content: dict
) -> str:
    """
    Grounded fallback answer built from the seeded topic content, so the tutor
    still teaches something useful with no API key and no internet.
    """
    label = STYLE_LABELS.get(style, "Standard")
    q = question.strip()
    parts = [
        f"(Offline tutor — {label} mode. Add GEMINI_API_KEY to .env for live AI answers.)",
        f"Good question about **{topic_name}**: \"{q}\"",
    ]

    intro = content.get("introduction")
    explanation = content.get("explanation")
    key_points = content.get("key_points")
    basic = content.get("basic_example")
    advanced = content.get("advanced_example")

    if intro:
        parts.append(f"\n**The core idea**\n{intro}")

    if explanation:
        # Keep it digestible in a chat bubble.
        excerpt = explanation if len(explanation) <= 900 else explanation[:900] + "..."
        parts.append(f"\n**Explanation**\n{excerpt}")

    if style == "slow":
        if basic:
            parts.append(f"\n**A simple example**\n{basic}")
        parts.append(
            "\nTake this one step at a time — re-read the explanation above, "
            "then try the quiz. You can retake it as many times as you need."
        )
    elif style == "fast":
        if advanced:
            parts.append(f"\n**Going deeper**\n{advanced}")
        parts.append(
            "\nSince you are moving quickly, focus on the edge cases and how "
            "this connects to the next topic."
        )
    else:
        if basic:
            parts.append(f"\n**Example**\n{basic}")
        if advanced:
            parts.append(f"\n**Advanced example**\n{advanced}")

    if key_points:
        parts.append(f"\n**Key points**\n{key_points}")

    parts.append(
        "\nWant me to go deeper on any part of this, or shall we move on to the quiz?"
    )
    return "\n".join(parts)


async def generate_quiz_questions(
    topic_name: str, topic_content: str, count: int = 10
) -> list[dict]:
    """Generate quiz questions for a topic, falling back to a built-in bank."""
    prompt = (
        f"Generate exactly {count} multiple-choice quiz questions for the topic: '{topic_name}'.\n"
        f"Topic content summary: {topic_content[:1000]}\n\n"
        "Return a JSON array of objects with this exact structure:\n"
        '[{"question": "...", "option_a": "...", "option_b": "...", '
        '"option_c": "...", "option_d": "...", "correct_answer": "A|B|C|D", '
        '"explanation": "..."}]\n\n'
        "Make questions that test understanding, not just memorization. "
        "Vary difficulty across questions. Return ONLY the JSON array, no other text."
    )
    result = await _call_gemini(prompt)
    if result:
        parsed = _parse_questions(result)
        if parsed:
            return parsed[:count]

    return _generate_hardcoded_questions(topic_name)


def _parse_questions(raw: str) -> list[dict]:
    """Parse a JSON array of questions out of a model response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = (
            "\n".join(lines[1:-1])
            if lines[-1].strip().startswith("```")
            else "\n".join(lines[1:])
        )

    try:
        questions = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        # Some models wrap the array in prose — grab the outermost [...] block.
        start, end = cleaned.find("["), cleaned.rfind("]")
        if start == -1 or end <= start:
            return []
        try:
            questions = json.loads(cleaned[start : end + 1])
        except (json.JSONDecodeError, TypeError):
            return []

    if not isinstance(questions, list):
        return []

    valid = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        required = ("question", "option_a", "option_b", "option_c", "option_d", "correct_answer")
        if not all(str(q.get(k, "")).strip() for k in required):
            continue
        if str(q["correct_answer"]).strip().upper() not in ("A", "B", "C", "D"):
            continue
        q["correct_answer"] = str(q["correct_answer"]).strip().upper()
        q.setdefault("explanation", "")
        valid.append(q)
    return valid


def _generate_hardcoded_questions(topic_name: str) -> list[dict]:
    """Fallback question bank used when Gemini is unavailable."""
    return [
        {
            "question": f"What is the primary focus of {topic_name}?",
            "option_a": "Understanding fundamental concepts",
            "option_b": "Memorizing definitions only",
            "option_c": "Writing code without understanding",
            "option_d": "Skipping theoretical foundations",
            "correct_answer": "A",
            "explanation": f"{topic_name} focuses on building a strong conceptual foundation.",
        },
        {
            "question": f"Which approach is best for learning {topic_name}?",
            "option_a": "Rush through all topics",
            "option_b": "Practice with hands-on examples",
            "option_c": "Only read textbooks",
            "option_d": "Skip difficult topics",
            "correct_answer": "B",
            "explanation": "Hands-on practice reinforces understanding of concepts.",
        },
        {
            "question": f"What is a key benefit of studying {topic_name}?",
            "option_a": "It has no real-world application",
            "option_b": "It improves problem-solving skills",
            "option_c": "It only helps in exams",
            "option_d": "It replaces other subjects",
            "correct_answer": "B",
            "explanation": "Studying this topic strengthens analytical and problem-solving abilities.",
        },
        {
            "question": f"In {topic_name}, what does 'fundamental' mean?",
            "option_a": "Optional knowledge",
            "option_b": "Advanced technique",
            "option_c": "Basic building block concept",
            "option_d": "Unrelated theory",
            "correct_answer": "C",
            "explanation": "Fundamentals are the basic building blocks that support advanced understanding.",
        },
        {
            "question": f"Which is NOT typically part of {topic_name}?",
            "option_a": "Core concepts",
            "option_b": "Practical applications",
            "option_c": "Cooking recipes",
            "option_d": "Theoretical foundations",
            "correct_answer": "C",
            "explanation": "Cooking recipes are unrelated to academic subjects.",
        },
        {
            "question": f"How should you approach a difficult concept in {topic_name}?",
            "option_a": "Give up immediately",
            "option_b": "Break it into smaller parts and study step by step",
            "option_c": "Skip it entirely",
            "option_d": "Memorize without understanding",
            "correct_answer": "B",
            "explanation": "Breaking complex concepts into smaller parts makes them easier to understand.",
        },
        {
            "question": f"What connects {topic_name} to real-world problems?",
            "option_a": "Nothing connects them",
            "option_b": "Practical applications and case studies",
            "option_c": "Only textbook examples",
            "option_d": "Random chance",
            "correct_answer": "B",
            "explanation": "Practical applications and case studies bridge theory and real-world use.",
        },
        {
            "question": f"What is the best way to retain knowledge of {topic_name}?",
            "option_a": "Cram before exams",
            "option_b": "Regular revision and practice",
            "option_c": "Read once and forget",
            "option_d": "Avoid the subject entirely",
            "correct_answer": "B",
            "explanation": "Spaced repetition and regular practice lead to long-term retention.",
        },
        {
            "question": f"In {topic_name}, what comes after understanding basics?",
            "option_a": "Nothing, basics are enough",
            "option_b": "Advanced concepts and applications",
            "option_c": "Starting over from scratch",
            "option_d": "Switching to a different field entirely",
            "correct_answer": "B",
            "explanation": "Once basics are solid, advancing to complex topics is the natural progression.",
        },
        {
            "question": f"Why is {topic_name} important in your curriculum?",
            "option_a": "It fills elective requirements",
            "option_b": "It builds essential skills for your field",
            "option_c": "It has no importance",
            "option_d": "It is only for advanced students",
            "correct_answer": "B",
            "explanation": "Core subjects build the essential skill set needed in your professional career.",
        },
    ]
