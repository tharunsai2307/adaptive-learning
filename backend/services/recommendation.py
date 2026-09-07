"""Recommendation engine — translates Q-Learning actions into human-readable guidance."""

from dataclasses import dataclass


@dataclass
class RecommendationResult:
    action: str
    title: str
    message: str
    teaching_style: str


_RECOMMENDATIONS = {
    "REVISION": RecommendationResult(
        action="REVISION",
        title="Revise This Topic",
        message=(
            "Your performance indicates that this topic needs reinforcement. "
            "Review the basic explanation and attempt another practice quiz."
        ),
        teaching_style="slow",
    ),
    "PRACTICE": RecommendationResult(
        action="PRACTICE",
        title="Practice More",
        message=(
            "You have a good understanding, but additional practice is recommended "
            "before moving forward. Try more exercises on this topic."
        ),
        teaching_style="normal",
    ),
    "CONTINUE": RecommendationResult(
        action="CONTINUE",
        title="Continue to Next Topic",
        message=(
            "Good job! You have demonstrated sufficient understanding. "
            "The system recommends moving to the next topic."
        ),
        teaching_style="normal",
    ),
    "ADVANCED": RecommendationResult(
        action="ADVANCED",
        title="Move to Advanced Topic",
        message=(
            "You have demonstrated a strong understanding. "
            "The system recommends moving to the advanced topic."
        ),
        teaching_style="fast",
    ),
}

# Teaching style descriptions for the adaptive AI teacher
TEACHING_STYLES = {
    "fast": {
        "label": "Accelerated",
        "progression": "Faster progression",
        "examples": "Advanced examples",
        "questions": "Higher difficulty questions",
        "explanation": "Less basic explanation, more conceptual depth",
    },
    "normal": {
        "label": "Standard",
        "progression": "Normal teaching speed",
        "examples": "More examples with medium difficulty",
        "questions": "Medium difficulty questions",
        "explanation": "Balanced explanation with additional practice",
    },
    "slow": {
        "label": "Supportive",
        "progression": "Slow progression with revision",
        "examples": "Simple, basic examples",
        "questions": "Easier questions to build confidence",
        "explanation": "Detailed simple explanations with revision material",
    },
}


def get_recommendation(action: str) -> RecommendationResult:
    """Return the recommendation for a given Q-Learning action."""
    return _RECOMMENDATIONS.get(action, _RECOMMENDATIONS["PRACTICE"])


def get_teaching_style(style_key: str) -> dict:
    """Return the adaptive teaching style configuration."""
    return TEACHING_STYLES.get(style_key, TEACHING_STYLES["normal"])
