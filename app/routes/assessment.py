import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser
from app.database import DbSession
from app.models import Assessment
from app.schemas.assessment import AssessmentResult, AssessmentSubmit, FormResponse
from app.services.assessment import AnswerError, compute_result, load_config, normalize_answers, public_form

router = APIRouter(prefix="/assessment", tags=["Assessment"])

# Mais recente primeiro (o id desempata avaliações feitas no mesmo milissegundo).
NEWEST_FIRST = (Assessment.created_at.desc(), Assessment.id.desc())


def _to_result(row: Assessment) -> AssessmentResult:
    return AssessmentResult(id=row.id, created_at=row.created_at, **json.loads(row.result))


@router.get("/form", response_model=FormResponse)
def get_form():
    """Perguntas e opções do formulário, lidas do assessment.json (rota pública)."""
    return public_form(load_config())


@router.post("", response_model=AssessmentResult, status_code=status.HTTP_201_CREATED)
def submit(data: AssessmentSubmit, user: CurrentUser, db: DbSession):
    """Recebe as respostas, calcula o resultado de acordo com o assessment.json e salva."""
    config = load_config()
    try:
        answers = normalize_answers(config, data.answers)
    except AnswerError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))

    result = compute_result(config, answers)
    row = Assessment(
        user_id=user.id,
        answers=json.dumps(answers, ensure_ascii=False),
        result=json.dumps(result, ensure_ascii=False),
        top_area=result["top_area"],
        version=config.version,
    )
    db.add(row)
    db.commit()
    return _to_result(row)


@router.get("/latest", response_model=AssessmentResult)
def latest(user: CurrentUser, db: DbSession):
    """Último resultado do usuário logado."""
    row = db.scalar(select(Assessment).where(Assessment.user_id == user.id).order_by(*NEWEST_FIRST).limit(1))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma avaliação encontrada.")
    return _to_result(row)


@router.get("/history", response_model=list[AssessmentResult])
def history(user: CurrentUser, db: DbSession):
    """Todas as avaliações do usuário logado, da mais recente para a mais antiga."""
    rows = db.scalars(select(Assessment).where(Assessment.user_id == user.id).order_by(*NEWEST_FIRST)).all()
    return [_to_result(r) for r in rows]
