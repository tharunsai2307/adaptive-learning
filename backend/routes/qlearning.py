from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.q_table import QTable
from ..models.quiz_attempt import QuizAttempt
from ..models.topic import Topic
from ..models.user import User
from ..auth import get_current_user
from ..services.q_learning import (
    ACTIONS,
    ALL_STATES,
    ALPHA,
    EPSILON,
    GAMMA,
    PERFORMANCE_LEVELS,
    LEARNING_SPEEDS,
    REWARD_MAP,
    initial_q,
)

router = APIRouter(prefix="/api/qlearning", tags=["q-learning"])


def _table_for(db: Session, user_id: int) -> dict[str, dict[str, float]]:
    """This student's full Q-table, with any missing cells filled from the prior."""
    rows = db.query(QTable).filter(QTable.user_id == user_id).all()
    table = {s: {a: initial_q(s, a) for a in ACTIONS} for s in ALL_STATES}
    for r in rows:
        if r.state in table and r.action in table[r.state]:
            table[r.state][r.action] = r.q_value
    return table


@router.get("/q-table")
def get_q_table(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get this student's full Q-table for visualisation."""
    table = _table_for(db, user.id)

    learned = {
        (r.state, r.action)
        for r in db.query(QTable).filter(QTable.user_id == user.id).all()
    }

    return {
        "user_id": user.id,
        "states": ALL_STATES,
        "actions": ACTIONS,
        "performance_levels": PERFORMANCE_LEVELS,
        "learning_speeds": LEARNING_SPEEDS,
        "table": table,
        "learned_cells": [
            {"state": s, "action": a} for (s, a) in sorted(learned)
        ],
        "hyperparameters": {"alpha": ALPHA, "gamma": GAMMA, "epsilon": EPSILON},
    }


@router.get("/last-decision")
def get_last_decision(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the last Q-Learning decision for the current user, with its Q-values."""
    last_attempt = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc(), QuizAttempt.id.desc())
        .first()
    )
    if not last_attempt:
        return {
            "message": "No quiz attempts yet. Complete a quiz to see Q-Learning in action!",
            "current_state": None,
        }

    state = f"{last_attempt.performance_level}_{last_attempt.learning_speed}"
    if state not in ALL_STATES:
        state = "Average_Normal"

    table = _table_for(db, user.id)
    q_values = table.get(state, {a: 0.0 for a in ACTIONS})

    topic = db.query(Topic).filter(Topic.id == last_attempt.topic_id).first()
    perf, _, speed = state.partition("_")

    return {
        "current_state": state,
        "performance_level": last_attempt.performance_level,
        "learning_speed": last_attempt.learning_speed,
        "chosen_action": last_attempt.rl_action,
        "accuracy": last_attempt.accuracy,
        "score": last_attempt.score,
        "total": last_attempt.total_questions,
        "time_taken": last_attempt.time_taken_seconds,
        "attempt_number": last_attempt.attempt_number,
        "topic": topic.name if topic else "",
        "reward": REWARD_MAP.get((perf, speed), 0),
        "q_values": q_values,
        "all_q_table": table,
        "hyperparameters": {"alpha": ALPHA, "gamma": GAMMA, "epsilon": EPSILON},
    }
