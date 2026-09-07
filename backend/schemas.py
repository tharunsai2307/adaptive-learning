"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, EmailStr
from typing import Optional


# ── Auth ───────────────────────────────────────────────────────────

class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# ── Profile ────────────────────────────────────────────────────────

class ProfileRequest(BaseModel):
    education: str = ""
    year: str = ""
    department: str = ""

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    education: str
    year: str
    department: str
    selected_subject_id: Optional[int] = None
    current_topic_index: int = 0
    learning_streak: int = 0

# ── Subject ────────────────────────────────────────────────────────

class SubjectResponse(BaseModel):
    id: int
    name: str
    department: str
    education: str
    year: str

# ── Topic ──────────────────────────────────────────────────────────

class TopicResponse(BaseModel):
    id: int
    name: str
    difficulty: str
    order_number: int
    description: str
    introduction: str
    explanation: str
    basic_example: str
    advanced_example: str
    key_points: str
    resources: str
    study_time_minutes: int

class TopicContentResponse(BaseModel):
    topic: TopicResponse
    teaching_style: str = "normal"

# ── Quiz ───────────────────────────────────────────────────────────

class QuestionResponse(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

class QuizSubmitRequest(BaseModel):
    topic_id: int
    answers: dict[str, str]  # {"question_id": "A", ...}
    time_taken_seconds: int

class QuizResultResponse(BaseModel):
    score: int
    total_questions: int
    accuracy: float
    time_taken_seconds: int
    performance_level: str
    learning_speed: str
    attempt_number: int
    rl_action: str
    recommendation: dict
    q_learning_viz: dict

# ── Tutor ──────────────────────────────────────────────────────────

class TutorRequest(BaseModel):
    topic_id: int
    question: str

class TutorResponse(BaseModel):
    answer: str

# ── Dashboard ──────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    student_name: str
    profile: dict
    stats: dict
    current_topic: Optional[dict] = None
    total_topics: int = 0
    recent_recommendation: Optional[dict] = None
    performance_history: list = []

# ── Q-Learning Viz ────────────────────────────────────────────────

class QLVisualizationResponse(BaseModel):
    current_state: str
    performance_level: str
    learning_speed: str
    chosen_action: str
    reward: int
    q_values: dict[str, float]
    all_q_table: dict
    next_state: str
    recommendation: dict
