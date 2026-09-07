from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class QTable(Base):
    __tablename__ = "q_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    state: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    q_value: Mapped[float] = mapped_column(Float, default=0.0)
