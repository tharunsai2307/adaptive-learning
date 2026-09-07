from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.question import Question
from ..models.topic import Topic
from ..models.quiz_attempt import QuizAttempt
from ..models.student_profile import StudentProfile
from ..models.recommendation import Recommendation
from ..models.user import User
from ..auth import decode_token
from ..schemas import QuizSubmitRequest
from ..services.performance import analyse_quiz
from ..services.q_learning import QLearningAgent
from ..services.recommendation import get_recommendation
from ..services.tutor import generate_quiz_questions

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def _get_user(authorization: str, db: Session) -> User:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/questions/{topic_id}")
async def get_questions(
    topic_id: int,
    authorization: str = Depends(lambda request: request.headers.get("Authorization", "")),
    db: Session = Depends(get_db),
):
    """Get quiz questions for a topic. Generates via Gemini if none exist."""
    user = _get_user(authorization, db)
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Check if questions already exist
    questions = db.query(Question).filter(Question.topic_id == topic_id).all()
    if not questions:
        # Generate questions via Gemini
        generated = await generate_quiz_questions(topic.name, topic.explanation or topic.description)
        for q_data in generated:
            q = Question(
                topic_id=topic_id,
                question=q_data["question"],
                option_a=q_data["option_a"],
                option_b=q_data["option_b"],
                option_c=q_data["option_c"],
                option_d=q_data["option_d"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation", ""),
            )
            db.add(q)
        db.commit()
        questions = db.query(Question).filter(Question.topic_id == topic_id).all()

    return [
        {
            "id": q.id,
            "question": q.question,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
        }
        for q in questions
    ]


@router.post("/submit")
def submit_quiz(
    body: QuizSubmitRequest,
    authorization: str = Depends(lambda request: request.headers.get("Authorization", "")),
    db: Session = Depends(get_db),
):
    """Submit quiz answers and get performance + Q-Learning results."""
    user = _get_user(authorization, db)
    topic = db.query(Topic).filter(Topic.id == body.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Grade the quiz
    questions = db.query(Question).filter(Question.topic_id == body.topic_id).all()
    score = 0
    for q in questions:
        q_id_str = str(q.id)
        if body.answers.get(q_id_str, "").upper() == q.correct_answer.upper():
            score += 1

    # Performance analysis
    result = analyse_quiz(
        db=db,
        user_id=user.id,
        topic_id=body.topic_id,
        score=score,
        total_questions=len(questions),
        time_taken_seconds=body.time_taken_seconds,
        study_time_minutes=topic.study_time_minutes,
    )

    # Q-Learning decision
    agent = QLearningAgent(db)
    decision = agent.decide(
        accuracy=result.accuracy,
        time_taken_seconds=result.time_taken_seconds,
        topic_study_time=topic.study_time_minutes * 60,
    )

    # Save quiz attempt
    attempt = QuizAttempt(
        user_id=user.id,
        topic_id=req.topic_id,
        score=result.score,
        total_questions=result.total_questions,
        accuracy=result.accuracy,
        time_taken_seconds=result.time_taken_seconds,
        performance_level=result.performance_level,
        learning_speed=result.learning_speed,
        attempt_number=result.attempt_number,
        rl_action=decision.chosen_action,
    )
    db.add(attempt)

    # Save recommendation
    rec = get_recommendation(decision.chosen_action)
    recommendation = Recommendation(
        user_id=user.id,
        topic_id=req.topic_id,
        action=decision.chosen_action,
        reason=rec.message,
    )
    db.add(recommendation)

    # Update profile progress if action is CONTINUE or ADVANCED
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if profile and decision.chosen_action in ("CONTINUE", "ADVANCED"):
        profile.current_topic_index += 1
        profile.learning_streak += 1
    elif profile and decision.chosen_action == "REVISION":
        profile.learning_streak = max(0, profile.learning_streak - 1)

    db.commit()

    return {
        "score": result.score,
        "total_questions": result.total_questions,
        "accuracy": result.accuracy,
        "time_taken_seconds": result.time_taken_seconds,
        "performance_level": result.performance_level,
        "learning_speed": result.learning_speed,
        "attempt_number": result.attempt_number,
        "rl_action": decision.chosen_action,
        "recommendation": {
            "action": rec.action,
            "title": rec.title,
            "message": rec.message,
            "teaching_style": rec.teaching_style,
        },
        "q_learning_viz": {
            "current_state": decision.current_state,
            "performance_level": decision.performance_level,
            "learning_speed": decision.learning_speed,
            "chosen_action": decision.chosen_action,
            "reward": decision.reward,
            "q_values": decision.q_values,
            "all_q_table": decision.all_q_table,
            "next_state": decision.next_state,
        },
    }
