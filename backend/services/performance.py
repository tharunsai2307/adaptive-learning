"""Performance analysis service — turns a finished quiz into a performance verdict."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from ..models.quiz_attempt import QuizAttempt
from .q_learning import classify_performance, classify_speed

__all__ = [
    "PerformanceResult",
    "classify_performance",
    "classify_speed",
    "analyse_quiz",
    "get_user_stats",
    "get_user_weak_topics",
]


@dataclass
class PerformanceResult:
    score: int
    total_questions: int
    accuracy: float
    time_taken_seconds: int
    average_seconds_per_question: float
    performance_level: str
    learning_speed: str
    attempt_number: int


def get_attempt_number(db: Session, user_id: int, topic_id: int) -> int:
    """Return the next attempt number for this user+topic."""
    count = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.topic_id == topic_id)
        .count()
    )
    return count + 1


def analyse_quiz(
    db: Session,
    user_id: int,
    topic_id: int,
    score: int,
    total_questions: int,
    time_taken_seconds: int,
) -> PerformanceResult:
    """Score a quiz attempt and return the performance result."""
    total = max(total_questions, 1)
    accuracy = (score / total) * 100
    return PerformanceResult(
        score=score,
        total_questions=total_questions,
        accuracy=round(accuracy, 2),
        time_taken_seconds=time_taken_seconds,
        average_seconds_per_question=round(time_taken_seconds / total, 1),
        performance_level=classify_performance(accuracy),
        learning_speed=classify_speed(time_taken_seconds, total_questions),
        attempt_number=get_attempt_number(db, user_id, topic_id),
    )


def get_user_stats(db: Session, user_id: int) -> dict:
    """Aggregate performance statistics for the dashboard."""
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
    if not attempts:
        return {
            "total_attempts": 0,
            "average_accuracy": 0,
            "topics_completed": 0,
            "best_score": 0,
            "worst_score": 0,
            "total_time_seconds": 0,
            "excellent_count": 0,
            "average_count": 0,
            "weak_count": 0,
        }

    accuracies = [a.accuracy for a in attempts]
    scores = [a.score for a in attempts]

    return {
        "total_attempts": len(attempts),
        "average_accuracy": round(sum(accuracies) / len(accuracies), 2),
        "topics_completed": len({a.topic_id for a in attempts}),
        "best_score": max(scores),
        "worst_score": min(scores),
        "total_time_seconds": sum(a.time_taken_seconds for a in attempts),
        "excellent_count": sum(1 for a in attempts if a.performance_level == "Excellent"),
        "average_count": sum(1 for a in attempts if a.performance_level == "Average"),
        "weak_count": sum(1 for a in attempts if a.performance_level == "Weak"),
    }


def get_user_weak_topics(db: Session, user_id: int, limit: int = 5) -> list[dict]:
    """
    Topics the student is currently weak on: those whose **most recent**
    attempt is still below 60% accuracy. Using the latest attempt (rather than
    the best ever) means a topic drops off the list once it has been mastered.
    """
    from ..models.topic import Topic

    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.created_at.asc(), QuizAttempt.id.asc())
        .all()
    )
    latest: dict[int, float] = {}
    for a in attempts:
        latest[a.topic_id] = a.accuracy

    weak = sorted(
        ((tid, acc) for tid, acc in latest.items() if acc < 60),
        key=lambda kv: kv[1],
    )[:limit]

    out = []
    for tid, acc in weak:
        topic = db.query(Topic).filter(Topic.id == tid).first()
        if topic:
            out.append(
                {
                    "topic_id": tid,
                    "name": topic.name,
                    "last_accuracy": acc,
                    "subject_id": topic.subject_id,
                }
            )
    return out
