import json

from fastapi import APIRouter, HTTPException, status
from prisma.models import Assessment

from app.core.deps import CurrentUser
from app.database import db
from app.schemas.assessment import AssessmentResult, AssessmentSubmit, FormResponse
from app.services.assessment import AnswerError, compute_result, load_config, normalize_answers, public_form

router = APIRouter(prefix="/assessment", tags=["Assessment"])


def _to_result(row: Assessment) -> AssessmentResult:
    return AssessmentResult(id=row.id, created_at=row.createdAt, **json.loads(row.result))


@router.get("/form", response_model=FormResponse)
async def get_form():
    """Perguntas e opções do formulário, lidas do assessment.json (rota pública)."""
    return public_form(load_config())


@router.post("", response_model=AssessmentResult, status_code=status.HTTP_201_CREATED)
async def submit(data: AssessmentSubmit, user: CurrentUser):
    """Recebe as respostas, calcula o resultado de acordo com o assessment.json e salva."""
    config = load_config()
    try:
        answers = normalize_answers(config, data.answers)
    except AnswerError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))

    result = compute_result(config, answers)
    row = await db.assessment.create(
        data={
            "userId": user.id,
            "answers": json.dumps(answers, ensure_ascii=False),
            "result": json.dumps(result, ensure_ascii=False),
            "topArea": result["top_area"],
            "version": config.version,
        }
    )
    return _to_result(row)


@router.get("/latest", response_model=AssessmentResult)
async def latest(user: CurrentUser):
    """Último resultado do usuário logado."""
    row = await db.assessment.find_first(where={"userId": user.id}, order={"createdAt": "desc"})
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma avaliação encontrada.")
    return _to_result(row)


@router.get("/history", response_model=list[AssessmentResult])
async def history(user: CurrentUser):
    """Todas as avaliações do usuário logado, da mais recente para a mais antiga."""
    rows = await db.assessment.find_many(where={"userId": user.id}, order={"createdAt": "desc"})
    return [_to_result(r) for r in rows]
