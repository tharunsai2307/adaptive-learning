from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.question import Question
from ..models.topic import Topic
from ..models.quiz_attempt import QuizAttempt
from ..models.student_profile import StudentProfile
from ..models.recommendation import Recommendation
from ..models.user import User
from ..auth import get_current_user
from ..schemas import QuizSubmitRequest
from ..services.performance import analyse_quiz
from ..services.q_learning import QLearningAgent, classify_performance
from ..services.recommendation import get_recommendation, get_teaching_style
from ..services.tutor import generate_quiz_questions

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

MAX_QUESTIONS_PER_QUIZ = 15


@router.get("/questions/{topic_id}")
async def get_questions(
    topic_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quiz questions for a topic. Generates them if the topic has none."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    questions = db.query(Question).filter(Question.topic_id == topic_id).all()
    if not questions:
        generated = await generate_quiz_questions(
            topic.name, topic.explanation or topic.description
        )
        for q_data in generated:
            db.add(
                Question(
                    topic_id=topic_id,
                    question=q_data["question"],
                    option_a=q_data["option_a"],
                    option_b=q_data["option_b"],
                    option_c=q_data["option_c"],
                    option_d=q_data["option_d"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data.get("explanation", ""),
                )
            )
        db.commit()
        questions = db.query(Question).filter(Question.topic_id == topic_id).all()

    questions = questions[:MAX_QUESTIONS_PER_QUIZ]

    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "total_questions": len(questions),
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
            }
            for q in questions
        ],
    }


@router.post("/submit")
def submit_quiz(
    body: QuizSubmitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit quiz answers and get performance analysis + the Q-Learning decision."""
    topic = db.query(Topic).filter(Topic.id == body.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # ── Grade ──────────────────────────────────────────────────────
    questions = db.query(Question).filter(Question.topic_id == body.topic_id).all()
    if not questions:
        raise HTTPException(
            status_code=400, detail="This topic has no quiz questions yet."
        )

    score = 0
    review = []
    for q in questions:
        given = (body.answers.get(str(q.id)) or "").strip().upper()
        correct = q.correct_answer.strip().upper()
        is_correct = given == correct
        score += int(is_correct)
        review.append(
            {
                "question_id": q.id,
                "question": q.question,
                "your_answer": given or None,
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": q.explanation,
            }
        )

    # ── Performance analysis ───────────────────────────────────────
    result = analyse_quiz(
        db=db,
        user_id=user.id,
        topic_id=body.topic_id,
        score=score,
        total_questions=len(questions),
        time_taken_seconds=body.time_taken_seconds,
    )

    # ── Reinforcement learning decision (per student) ──────────────
    agent = QLearningAgent(db, user_id=user.id)
    decision = agent.decide(
        accuracy=result.accuracy,
        time_taken_seconds=result.time_taken_seconds,
        total_questions=result.total_questions,
    )

    # ── Persist ────────────────────────────────────────────────────
    db.add(
        QuizAttempt(
            user_id=user.id,
            topic_id=body.topic_id,
            score=result.score,
            total_questions=result.total_questions,
            accuracy=result.accuracy,
            time_taken_seconds=result.time_taken_seconds,
            performance_level=result.performance_level,
            learning_speed=result.learning_speed,
            attempt_number=result.attempt_number,
            rl_action=decision.chosen_action,
        )
    )

    rec = get_recommendation(decision.chosen_action)
    db.add(
        Recommendation(
            user_id=user.id,
            topic_id=body.topic_id,
            action=decision.chosen_action,
            reason=rec.message,
        )
    )

    # ── Advance the personalized learning path ─────────────────────
    profile = (
        db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    )
    moved_to_next = False
    if profile:
        if decision.chosen_action in ("CONTINUE", "ADVANCED"):
            profile.current_topic_index += 1
            profile.learning_streak += 1
            moved_to_next = True
        elif decision.chosen_action == "REVISION":
            profile.learning_streak = 0
    db.commit()

    next_topic = None
    if profile and profile.selected_subject_id:
        topics = (
            db.query(Topic)
            .filter(Topic.subject_id == profile.selected_subject_id)
            .order_by(Topic.order_number)
            .all()
        )
        if 0 <= profile.current_topic_index < len(topics):
            nt = topics[profile.current_topic_index]
            next_topic = {
                "id": nt.id,
                "name": nt.name,
                "difficulty": nt.difficulty,
                "order_number": nt.order_number,
            }

    return {
        "score": result.score,
        "total_questions": result.total_questions,
        "accuracy": result.accuracy,
        "time_taken_seconds": result.time_taken_seconds,
        "average_seconds_per_question": result.average_seconds_per_question,
        "performance_level": result.performance_level,
        "learning_speed": result.learning_speed,
        "attempt_number": result.attempt_number,
        "rl_action": decision.chosen_action,
        "review": review,
        "recommendation": {
            "action": rec.action,
            "title": rec.title,
            "message": rec.message,
            "teaching_style": rec.teaching_style,
            "teaching_style_detail": get_teaching_style(rec.teaching_style),
        },
        "next_topic": next_topic,
        "moved_to_next": moved_to_next,
        "q_learning_viz": {
            "current_state": decision.current_state,
            "performance_level": decision.performance_level,
            "learning_speed": decision.learning_speed,
            "chosen_action": decision.chosen_action,
            "reward": decision.reward,
            "q_values": decision.q_values,
            "q_values_before": decision.q_values_before,
            "q_value_after": decision.q_value_after,
            "max_next_q": decision.max_next_q,
            "all_q_table": decision.all_q_table,
            "next_state": decision.next_state,
            "explored": decision.explored,
            "allowed_actions": decision.allowed_actions,
            "alpha": decision.alpha,
            "gamma": decision.gamma,
            "epsilon": decision.epsilon,
        },
    }


@router.get("/result/{topic_id}")
def last_result(
    topic_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """The student's most recent attempt for a topic, with a re-graded review."""
    attempt = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.topic_id == topic_id,
        )
        .order_by(QuizAttempt.created_at.desc(), QuizAttempt.id.desc())
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="No attempt found for this topic")

    rec = get_recommendation(attempt.rl_action)
    return {
        "topic_id": topic_id,
        "score": attempt.score,
        "total_questions": attempt.total_questions,
        "accuracy": attempt.accuracy,
        "time_taken_seconds": attempt.time_taken_seconds,
        "performance_level": attempt.performance_level,
        "learning_speed": attempt.learning_speed,
        "attempt_number": attempt.attempt_number,
        "rl_action": attempt.rl_action,
        "recommendation": {
            "action": rec.action,
            "title": rec.title,
            "message": rec.message,
            "teaching_style": rec.teaching_style,
        },
        "created_at": attempt.created_at.isoformat() if attempt.created_at else "",
    }
