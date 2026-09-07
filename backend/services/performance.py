"""Performance analysis service."""

from dataclasses import dataclass
from sqlalchemy.orm import Session

from ..models.quiz_attempt import QuizAttempt


@dataclass
class PerformanceResult:
    score: int
    total_questions: int
    accuracy: float
    time_taken_seconds: int
    performance_level: str
    learning_speed: str
    attempt_number: int


def classify_performance(accuracy: float) -> str:
    if accuracy >= 80:
        return "Excellent"
    elif accuracy >= 60:
        return "Average"
    return "Weak"


def classify_speed(time_taken: int, study_time: int) -> str:
    ratio = time_taken / max(study_time, 1)
    if ratio <= 0.5:
        return "Fast"
    elif ratio <= 1.0:
        return "Normal"
    return "Slow"


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
    study_time_minutes: int,
) -> PerformanceResult:
    """Score a quiz attempt and return the performance result."""
    accuracy = (score / max(total_questions, 1)) * 100
    perf_level = classify_performance(accuracy)
    speed = classify_speed(time_taken_seconds, study_time_minutes * 60)
    attempt_num = get_attempt_number(db, user_id, topic_id)

    return PerformanceResult(
        score=score,
        total_questions=total_questions,
        accuracy=round(accuracy, 2),
        time_taken_seconds=time_taken_seconds,
        performance_level=perf_level,
        learning_speed=speed,
        attempt_number=attempt_num,
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
            "excellent_count": 0,
            "average_count": 0,
            "weak_count": 0,
        }

    accuracies = [a.accuracy for a in attempts]
    scores = [a.score for a in attempts]
    topics = set(a.topic_id for a in attempts)

    return {
        "total_attempts": len(attempts),
        "average_accuracy": round(sum(accuracies) / len(accuracies), 2),
        "topics_completed": len(topics),
        "best_score": max(scores),
        "worst_score": min(scores),
        "excellent_count": sum(1 for a in attempts if a.performance_level == "Excellent"),
        "average_count": sum(1 for a in attempts if a.performance_level == "Average"),
        "weak_count": sum(1 for a in attempts if a.performance_level == "Weak"),
    }
