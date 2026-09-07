from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    education: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[str] = mapped_column(String(20), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    selected_subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id"), nullable=True
    )
    current_topic_index: Mapped[int] = mapped_column(default=0)
    learning_streak: Mapped[int] = mapped_column(default=0)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    selected_subject: Mapped["Subject"] = relationship("Subject", foreign_keys=[selected_subject_id])
