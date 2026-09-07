"""
Subject curriculum content.

Keyed by **subject name** rather than subject id, because the seed data
deliberately creates the same subject for several education/year/department
combinations (e.g. "Python Programming" for both B.Tech and BCA). Keying by
name lets every matching Subject row get the same lessons and questions.
"""

from . import (
    computer_networks,
    data_structures,
    dbms,
    operating_systems,
    python_programming,
)

CURRICULUM: dict[str, dict] = {
    "Python Programming": {
        "topics": python_programming.TOPICS,
        "questions": python_programming.QUESTIONS,
    },
    "Data Structures": {
        "topics": data_structures.TOPICS,
        "questions": data_structures.QUESTIONS,
    },
    "Database Management Systems": {
        "topics": dbms.TOPICS,
        "questions": dbms.QUESTIONS,
    },
    "Computer Networks": {
        "topics": computer_networks.TOPICS,
        "questions": computer_networks.QUESTIONS,
    },
    "Operating Systems": {
        "topics": operating_systems.TOPICS,
        "questions": operating_systems.QUESTIONS,
    },
}


def curriculum_for(subject_name: str) -> dict | None:
    """Return the {topics, questions} bundle for a subject, or None."""
    return CURRICULUM.get(subject_name)
