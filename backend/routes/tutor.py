from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.topic import Topic
from ..models.user import User
from ..auth import decode_token
from ..schemas import TutorRequest, TutorResponse
from ..services.tutor import ask_tutor

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


def _get_user(authorization: str, db: Session) -> User:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/ask", response_model=TutorResponse)
async def ask_question(
    body: TutorRequest,
    authorization: str = Depends(lambda request: request.headers.get("Authorization", "")),
    db: Session = Depends(get_db),
):
    """Ask the AI tutor a question about a topic."""
    user = _get_user(authorization, db)
    topic = db.query(Topic).filter(Topic.id == body.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    answer = await ask_tutor(topic.name, body.question, teaching_style="normal")
    return TutorResponse(answer=answer)
