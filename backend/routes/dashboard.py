from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.topic import Topic
from ..models.quiz_attempt import QuizAttempt
from ..models.recommendation import Recommendation
from ..auth import decode_token
from ..services.performance import get_user_stats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _get_user(authorization: str, db: Session) -> User:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/")
def get_dashboard(
    authorization: str = Depends(lambda request: request.headers.get("Authorization", "")),
    db: Session = Depends(get_db),
):
    """Get full dashboard data for the current student."""
    user = _get_user(authorization, db)
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()

    stats = get_user_stats(db, user.id)

    # Current topic
    current_topic = None
    total_topics = 0
    if profile and profile.selected_subject_id:
        topics = (
            db.query(Topic)
            .filter(Topic.subject_id == profile.selected_subject_id)
            .order_by(Topic.order_number)
            .all()
        )
        total_topics = len(topics)
        if 0 <= profile.current_topic_index < len(topics):
            t = topics[profile.current_topic_index]
            current_topic = {
                "id": t.id,
                "name": t.name,
                "difficulty": t.difficulty,
                "order_number": t.order_number,
            }

    # Recent recommendation
    recent_rec = None
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user.id)
        .order_by(Recommendation.created_at.desc())
        .first()
    )
    if rec:
        from ..services.recommendation import get_recommendation
        rec_data = get_recommendation(rec.action)
        recent_rec = {
            "action": rec.action,
            "title": rec_data.title,
            "message": rec.reason,
        }

    # Performance history
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc())
        .limit(20)
        .all()
    )
    history = []
    for a in attempts:
        topic = db.query(Topic).filter(Topic.id == a.topic_id).first()
        history.append({
            "date": a.created_at.isoformat() if a.created_at else "",
            "topic": topic.name if topic else "Unknown",
            "score": a.score,
            "total": a.total_questions,
            "accuracy": a.accuracy,
            "time_taken": a.time_taken_seconds,
            "performance": a.performance_level,
            "rl_action": a.rl_action,
        })

    return {
        "student_name": user.name,
        "profile": {
            "education": profile.education if profile else "",
            "year": profile.year if profile else "",
            "department": profile.department if profile else "",
            "learning_streak": profile.learning_streak if profile else 0,
        },
        "stats": stats,
        "current_topic": current_topic,
        "total_topics": total_topics,
        "recent_recommendation": recent_rec,
        "performance_history": history,
    }


@router.get("/performance-history")
def performance_history(
    authorization: str = Depends(lambda request: request.headers.get("Authorization", "")),
    db: Session = Depends(get_db),
):
    """Get full performance history table."""
    user = _get_user(authorization, db)
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc())
        .all()
    )
    history = []
    for a in attempts:
        topic = db.query(Topic).filter(Topic.id == a.topic_id).first()
        history.append({
            "id": a.id,
            "date": a.created_at.isoformat() if a.created_at else "",
            "topic": topic.name if topic else "Unknown",
            "score": a.score,
            "total": a.total_questions,
            "accuracy": a.accuracy,
            "time_taken": a.time_taken_seconds,
            "performance": a.performance_level,
            "rl_action": a.rl_action,
            "attempt_number": a.attempt_number,
        })
    return history
