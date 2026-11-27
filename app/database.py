"""
Conexão com o banco via SQLAlchemy.

Em produção o banco é o PostgreSQL do Supabase, acessado pelo pooler em modo transaction (porta 6543).
"""

from collections.abc import Iterator
from typing import Annotated
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

# Parâmetros que só o Prisma entendia. O psycopg recusa parâmetros desconhecidos na URL,
# então eles são removidos: assim a mesma DATABASE_URL de antes continua funcionando.
_PRISMA_ONLY_PARAMS = {"pgbouncer", "connection_limit", "pool_timeout"}


def normalize_database_url(url: str) -> str:
    """`postgresql://...?pgbouncer=true` (formato do Prisma) → `postgresql+psycopg://...`."""
    parts = urlsplit(url)
    scheme = "postgresql+psycopg" if parts.scheme in ("postgres", "postgresql") else parts.scheme
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if k not in _PRISMA_ONLY_PARAMS])
    return urlunsplit((scheme, parts.netloc, parts.path, query, parts.fragment))


def make_engine(url: str) -> Engine:
    url = normalize_database_url(url)
    if url.startswith("postgresql"):
        return create_engine(
            url,
            # Sem pool local: cada requisição abre e fecha a sua conexão e quem faz o pool é o Supabase.
            # Na Vercel a função "congela" entre requisições, e conexões guardadas num pool morreriam.
            poolclass=NullPool,
            # O pooler em modo transaction não suporta prepared statements.
            connect_args={"prepare_threshold": None},
        )
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)


# create_engine não conecta ainda: a primeira conexão só acontece na primeira consulta.
engine = make_engine(get_settings().database_url)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """Dependência do FastAPI: uma sessão por requisição, fechada no fim."""
    with SessionLocal() as db:
        yield db


DbSession = Annotated[Session, Depends(get_db)]
