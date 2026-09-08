from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.topic import Topic
from ..models.recommendation import Recommendation
from ..models.user import User
from ..auth import get_current_user
from ..schemas import TutorRequest, TutorResponse
from ..services.recommendation import get_recommendation
from ..services.tutor import ask_tutor, is_gemini_configured

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


def _adaptive_style(db: Session, user_id: int) -> str:
    """
    The AI teacher adapts to the student's most recent Q-Learning decision:
      Weak  -> REVISION -> "slow"   (simpler language, smaller steps)
      Average -> PRACTICE -> "normal"
      Strong -> CONTINUE/ADVANCED -> "fast" (concise, deeper)
    """
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.created_at.desc(), Recommendation.id.desc())
        .first()
    )
    if not rec:
        return "normal"
    return get_recommendation(rec.action).teaching_style


@router.get("/status")
def tutor_status():
    """Tell the client whether live Gemini answers are configured."""
    return {"gemini_configured": is_gemini_configured()}


@router.post("/ask", response_model=TutorResponse)
async def ask_question(
    body: TutorRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ask the AI tutor a question about a topic."""
    topic = db.query(Topic).filter(Topic.id == body.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    style = body.teaching_style or _adaptive_style(db, user.id)

    content = {
        "introduction": topic.introduction,
        "explanation": topic.explanation,
        "basic_example": topic.basic_example,
        "advanced_example": topic.advanced_example,
        "key_points": topic.key_points,
    }

    answer, source = await ask_tutor(
        topic.name, body.question, teaching_style=style, topic_content=content
    )
    return TutorResponse(answer=answer, teaching_style=style, source=source)
