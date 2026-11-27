import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.config import get_settings
from app.database import DbSession
from app.routes import assessment, auth, users

logger = logging.getLogger("facmap")

settings = get_settings()

app = FastAPI(title="FacMap API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assessment.router)

DB_UNAVAILABLE = "Banco de dados indisponível. Tente novamente em instantes."


@app.exception_handler(OperationalError)
async def database_unavailable(_: Request, exc: OperationalError):
    """Banco fora do ar ou URL errada: responde 503 com mensagem (e com CORS), em vez de um 500 sem corpo."""
    logger.error("Falha ao acessar o banco: %s", exc.orig)
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": DB_UNAVAILABLE})


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.get("/health/db", tags=["Health"])
def health_db(db: DbSession):
    """Confere se a API consegue falar com o banco (útil depois de um deploy)."""
    db.execute(text("select 1"))
    return {"status": "ok", "database": "ok"}
