from datetime import datetime

from sqlalchemy import Boolean, Index, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.types import UTCDateTime, utcnow


class User(Base):
    # Nomes de tabela, colunas e índices iguais aos criados pelo Prisma, para usar o banco que já existe.
    __tablename__ = "users"
    __table_args__ = (Index("users_email_key", "email", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    hashed_password: Mapped[str] = mapped_column("hashedPassword", Text)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", UTCDateTime, default=utcnow, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column("updatedAt", UTCDateTime, default=utcnow, onupdate=utcnow)
