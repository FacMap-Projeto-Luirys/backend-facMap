from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import TypeDecorator


def utcnow() -> datetime:
    """Agora em UTC, cortado em milissegundos (a precisão da coluna TIMESTAMP(3))."""
    now = datetime.now(timezone.utc)
    return now.replace(microsecond=now.microsecond // 1000 * 1000)


class UTCDateTime(TypeDecorator):
    """Data e hora em UTC.

    Grava sem fuso em TIMESTAMP(3), como o Prisma gravava, e devolve com fuso UTC.
    Assim a API continua respondendo `created_at` no mesmo formato de antes.
    """

    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return postgresql.TIMESTAMP(precision=3)
        return dialect.type_descriptor(DateTime())

    def process_bind_param(self, value: datetime | None, dialect):
        if value is not None and value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value: datetime | None, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value
