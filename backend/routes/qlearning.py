from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.q_table import QTable
from ..models.quiz_attempt import QuizAttempt
from ..models.user import User
from ..auth import decode_token
from ..services.q_learning import QLearningAgent, ACTIONS, ALL_STATES

router = APIRouter(prefix="/api/qlearning", tags=["q-learning"])


def _get_user(authorization: str, db: Session) -> User:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/q-table")
def get_q_table(
    authorization: str = Depends(lambda request: request.headers.get("Authorization", "")),
    db: Session = Depends(get_db),
):
    """Get the full Q-table for visualisation."""
    user = _get_user(authorization, db)
    rows = db.query(QTable).all()
    table = {}
    for r in rows:
        table.setdefault(r.state, {})[r.action] = r.q_value

    # Ensure all states are present
    for s in ALL_STATES:
        if s not in table:
            table[s] = {a: 0.0 for a in ACTIONS}

    return {
        "states": ALL_STATES,
        "actions": ACTIONS,
        "table": table,
    }


@router.get("/last-decision")
def get_last_decision(
    authorization: str = Depends(lambda request: request.headers.get("Authorization", "")),
    db: Session = Depends(get_db),
):
    """Get the last Q-Learning decision for the current user."""
    user = _get_user(authorization, db)
    last_attempt = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc())
        .first()
    )
    if not last_attempt:
        return {"message": "No quiz attempts yet. Complete a quiz to see Q-Learning in action!"}

    return {
        "current_state": f"{last_attempt.performance_level}_{last_attempt.learning_speed}",
        "performance_level": last_attempt.performance_level,
        "learning_speed": last_attempt.learning_speed,
        "chosen_action": last_attempt.rl_action,
        "accuracy": last_attempt.accuracy,
        "score": last_attempt.score,
        "total": last_attempt.total_questions,
    }
