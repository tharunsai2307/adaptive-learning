from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), default="medium")
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    introduction: Mapped[str] = mapped_column(Text, default="")
    explanation: Mapped[str] = mapped_column(Text, default="")
    basic_example: Mapped[str] = mapped_column(Text, default="")
    advanced_example: Mapped[str] = mapped_column(Text, default="")
    key_points: Mapped[str] = mapped_column(Text, default="")
    resources: Mapped[str] = mapped_column(Text, default="")
    study_time_minutes: Mapped[int] = mapped_column(Integer, default=30)

    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="topics")
    questions: Mapped[list["Question"]] = relationship(
        "Question", back_populates="topic", cascade="all, delete-orphan"
    )
