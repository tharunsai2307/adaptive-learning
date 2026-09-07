from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.subject import Subject
from ..models.topic import Topic
from ..models.quiz_attempt import QuizAttempt
from ..models.recommendation import Recommendation
from ..auth import get_current_user
from ..services.performance import (
    get_user_stats,
    get_user_weak_topics,
)
from ..services.recommendation import get_recommendation, get_teaching_style

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full dashboard data for the current student."""
    profile = (
        db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    )
    stats = get_user_stats(db, user.id)
    weak_topics = get_user_weak_topics(db, user.id)

    # Current topic + subject
    current_topic = None
    subject_name = ""
    total_topics = 0
    completed_topics = 0
    if profile and profile.selected_subject_id:
        subject = (
            db.query(Subject).filter(Subject.id == profile.selected_subject_id).first()
        )
        subject_name = subject.name if subject else ""
        topics = (
            db.query(Topic)
            .filter(Topic.subject_id == profile.selected_subject_id)
            .order_by(Topic.order_number)
            .all()
        )
        total_topics = len(topics)
        completed_topics = min(profile.current_topic_index, total_topics)
        if 0 <= profile.current_topic_index < len(topics):
            t = topics[profile.current_topic_index]
            current_topic = {
                "id": t.id,
                "name": t.name,
                "difficulty": t.difficulty,
                "order_number": t.order_number,
            }

    # Most recent Q-Learning recommendation
    recent_rec = None
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user.id)
        .order_by(Recommendation.created_at.desc(), Recommendation.id.desc())
        .first()
    )
    if rec:
        rec_data = get_recommendation(rec.action)
        recent_rec = {
            "action": rec.action,
            "title": rec_data.title,
            "message": rec.reason or rec_data.message,
            "teaching_style": rec_data.teaching_style,
            "teaching_style_label": get_teaching_style(rec_data.teaching_style)["label"],
            "topic_id": rec.topic_id,
        }

    # Performance history (most recent first)
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc(), QuizAttempt.id.desc())
        .limit(20)
        .all()
    )
    history = []
    for a in attempts:
        topic = db.query(Topic).filter(Topic.id == a.topic_id).first()
        history.append(
            {
                "id": a.id,
                "date": a.created_at.isoformat() if a.created_at else "",
                "topic": topic.name if topic else "Unknown",
                "score": a.score,
                "total": a.total_questions,
                "accuracy": a.accuracy,
                "time_taken": a.time_taken_seconds,
                "performance": a.performance_level,
                "rl_action": a.rl_action,
            }
        )

    return {
        "student_name": user.name,
        "profile": {
            "education": profile.education if profile else "",
            "year": profile.year if profile else "",
            "department": profile.department if profile else "",
            "learning_streak": profile.learning_streak if profile else 0,
            "subject": subject_name,
            "completed_topics": completed_topics,
            "total_topics": total_topics,
        },
        "stats": stats,
        "current_topic": current_topic,
        "total_topics": total_topics,
        "weak_topics": weak_topics,
        "recent_recommendation": recent_rec,
        "performance_history": history,
    }


@router.get("/performance-history")
def performance_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the full performance history table."""
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc(), QuizAttempt.id.desc())
        .all()
    )
    history = []
    for a in attempts:
        topic = db.query(Topic).filter(Topic.id == a.topic_id).first()
        history.append(
            {
                "id": a.id,
                "date": a.created_at.isoformat() if a.created_at else "",
                "topic": topic.name if topic else "Unknown",
                "topic_id": a.topic_id,
                "score": a.score,
                "total": a.total_questions,
                "accuracy": a.accuracy,
                "time_taken": a.time_taken_seconds,
                "performance": a.performance_level,
                "learning_speed": a.learning_speed,
                "rl_action": a.rl_action,
                "attempt_number": a.attempt_number,
            }
        )
    return history
