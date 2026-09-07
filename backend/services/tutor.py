"""AI Tutor service — uses Google Gemini API for chat and quiz generation."""

import json
import httpx
from ..config import settings

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


async def _call_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    if not settings.GEMINI_API_KEY:
        return _mock_response(prompt)

    async with httpx.AsyncClient(timeout=60) as client:
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
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "I'm sorry, I couldn't generate a response. Please try again."


def _mock_response(prompt: str) -> str:
    """Fallback mock response when no API key is configured."""
    lower = prompt.lower()
    if "quiz" in lower or "question" in lower:
        return json.dumps(_generate_mock_questions())
    if "explain" in lower or "what is" in lower:
        return (
            "That's a great question! Let me explain this concept step by step. "
            "The key idea here is to understand the fundamental principles first, "
            "then build on them with practical examples. "
            "Would you like me to go deeper into any specific aspect?"
        )
    return (
        "I understand your question. Based on the current topic, "
        "here's what you should focus on: the core concepts, "
        "practical applications, and how this connects to what you've "
        "already learned. Let me know if you'd like more examples!"
    )


async def ask_tutor(topic_name: str, question: str, teaching_style: str = "normal") -> str:
    """Ask the AI tutor a question about the current topic."""
    style_hints = {
        "fast": "Use advanced language, assume strong prior knowledge, be concise.",
        "normal": "Use clear language with moderate detail and examples.",
        "slow": "Use very simple language, break concepts into small steps, give basic examples.",
    }
    style_hint = style_hints.get(teaching_style, style_hints["normal"])

    prompt = (
        f"You are an AI tutor for the topic: '{topic_name}'.\n"
        f"Teaching style: {style_hint}\n\n"
        f"Student question: {question}\n\n"
        "Provide a clear, helpful, and encouraging answer. "
        "Use examples where appropriate."
    )
    return await _call_gemini(prompt)


async def generate_quiz_questions(topic_name: str, topic_content: str, count: int = 10) -> list[dict]:
    """Generate quiz questions for a topic using Gemini."""
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

    # Try to parse JSON from the response
    try:
        # Strip markdown code fences if present
        cleaned = result.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        questions = json.loads(cleaned)
        if isinstance(questions, list) and len(questions) > 0:
            return questions[:count]
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback to hardcoded questions
    return _generate_hardcoded_questions(topic_name)


def _generate_mock_questions() -> list[dict]:
    return _generate_hardcoded_questions("General")


def _generate_hardcoded_questions(topic_name: str) -> list[dict]:
    """Fallback hardcoded questions for when Gemini is unavailable."""
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
