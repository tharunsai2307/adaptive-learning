"""Pydantic schemas for request/response validation."""

from typing import Optional

from pydantic import BaseModel, Field


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
    topic_count: int = 0


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
    answers: dict[str, str] = Field(default_factory=dict)  # {"question_id": "A", ...}
    time_taken_seconds: int = 0


# ── Tutor ──────────────────────────────────────────────────────────

class TutorRequest(BaseModel):
    topic_id: int
    question: str
    teaching_style: Optional[str] = None  # fast | normal | slow (auto if omitted)


class TutorResponse(BaseModel):
    answer: str
    teaching_style: str = "normal"
    source: str = "offline"  # gemini | offline


# ── Dashboard ──────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    student_name: str
    profile: dict
    stats: dict
    current_topic: Optional[dict] = None
    total_topics: int = 0
    weak_topics: list = []
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
