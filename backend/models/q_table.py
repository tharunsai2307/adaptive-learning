from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class QTable(Base):
    """
    One row per (student, state, action).

    The Q-table is scoped per student so that each learner accumulates their
    own experience — student A's weak quiz must not change student B's
    recommendations. `user_id = 0` is used as a fallback for rows created
    before the per-student split.
    """

    __tablename__ = "q_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, default=0, index=True
    )
    state: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    q_value: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="q_rows")
