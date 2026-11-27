from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.types import UTCDateTime, utcnow


class Assessment(Base):
    """Cada envio do formulário de avaliação.

    `answers` e `result` guardam JSON serializado em texto (o código usa json.dumps/json.loads).
    """

    __tablename__ = "assessments"
    __table_args__ = (Index("assessments_userId_createdAt_idx", "userId", "createdAt"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        "userId",
        Integer,
        ForeignKey("users.id", name="assessments_userId_fkey", ondelete="CASCADE", onupdate="CASCADE"),
    )
    answers: Mapped[str] = mapped_column(Text)
    result: Mapped[str] = mapped_column(Text)
    top_area: Mapped[str] = mapped_column("topArea", Text)
    version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", UTCDateTime, default=utcnow, server_default=text("CURRENT_TIMESTAMP")
    )
