from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.topic import Topic
from ..models.subject import Subject
from ..models.student_profile import StudentProfile
from ..models.user import User
from ..auth import get_current_user

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("/")
def list_topics(
    subject_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all topics for a subject, ordered by order_number."""
    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.order_number)
        .all()
    )
    return [
        {
            "id": t.id,
            "name": t.name,
            "difficulty": t.difficulty,
            "order_number": t.order_number,
            "description": t.description,
        }
        for t in topics
    ]


# NOTE: this must be registered BEFORE "/{topic_id}", otherwise FastAPI matches
# "learning-path" as the {topic_id} path parameter and returns a 422.
@router.get("/learning-path/{subject_id}")
def learning_path(
    subject_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the student's personalized learning path with progress status."""
    profile = (
        db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    )
    current_idx = profile.current_topic_index if profile else 0

    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.order_number)
        .all()
    )

    path = []
    for i, t in enumerate(topics):
        if i < current_idx:
            status = "completed"
        elif i == current_idx:
            status = "current"
        else:
            status = "locked"
        path.append(
            {
                "id": t.id,
                "name": t.name,
                "difficulty": t.difficulty,
                "order_number": t.order_number,
                "status": status,
                "description": t.description,
            }
        )

    total = len(topics)
    completed = sum(1 for p in path if p["status"] == "completed")

    return {
        "subject_id": subject_id,
        "topics": path,
        "total_topics": total,
        "completed": completed,
        "remaining": total - completed,
        "progress_percent": round((completed / max(total, 1)) * 100, 1),
        "current_index": current_idx,
        "current_topic": next((p for p in path if p["status"] == "current"), None),
    }


@router.get("/{topic_id}")
def get_topic(
    topic_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full topic content for the AI tutor."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()

    return {
        "id": topic.id,
        "name": topic.name,
        "difficulty": topic.difficulty,
        "order_number": topic.order_number,
        "description": topic.description,
        "introduction": topic.introduction,
        "explanation": topic.explanation,
        "basic_example": topic.basic_example,
        "advanced_example": topic.advanced_example,
        "key_points": topic.key_points,
        "resources": topic.resources,
        "study_time_minutes": topic.study_time_minutes,
        "subject": subject.name if subject else "",
    }
