from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# ─── Estrutura do arquivo app/data/assessment.json ───────────────────────────


class AreaConfig(BaseModel):
    title: str
    desc: str
    icon: str
    color: str


class OptionConfig(BaseModel):
    value: str
    weights: dict[str, float] = {}
    exclusive: bool = False


class QuestionConfig(BaseModel):
    id: str
    label: str
    type: Literal["single", "multiple"]
    required: bool = True
    options: list[OptionConfig] = Field(min_length=1)


class WhyItem(BaseModel):
    icon: str
    text: str


class Discipline(BaseModel):
    name: str
    text: str


class PdiItem(BaseModel):
    period: str
    task: str
    color: str


class AreaResultConfig(BaseModel):
    why: list[WhyItem]
    discipline: Discipline
    pdi: list[PdiItem]


class ScoringConfig(BaseModel):
    base_pct: float = Field(30, ge=0, lt=100)
    top_n: int = Field(2, ge=1)


class AssessmentConfig(BaseModel):
    version: int
    scoring: ScoringConfig = ScoringConfig()
    areas: dict[str, AreaConfig] = Field(min_length=1)
    questions: list[QuestionConfig]
    results: dict[str, AreaResultConfig]

    @model_validator(mode="after")
    def check_consistency(self):
        """Pega erros de digitação no JSON ao carregar, em vez de no meio de uma requisição."""
        areas = set(self.areas)
        if missing := areas - set(self.results):
            raise ValueError(f"'results' sem as áreas: {sorted(missing)}")
        ids = [q.id for q in self.questions]
        if len(ids) != len(set(ids)):
            raise ValueError("Há perguntas com 'id' repetido")
        for q in self.questions:
            values = [o.value for o in q.options]
            if len(values) != len(set(values)):
                raise ValueError(f"Pergunta '{q.id}' tem opções repetidas")
            for opt in q.options:
                if unknown := set(opt.weights) - areas:
                    raise ValueError(f"Pergunta '{q.id}', opção '{opt.value}': áreas desconhecidas {sorted(unknown)}")
        return self


# ─── API ─────────────────────────────────────────────────────────────────────


class FormOption(BaseModel):
    value: str
    exclusive: bool = False


class FormQuestion(BaseModel):
    id: str
    label: str
    type: Literal["single", "multiple"]
    required: bool
    options: list[FormOption]


class FormResponse(BaseModel):
    version: int
    areas: dict[str, AreaConfig]
    questions: list[FormQuestion]


class AssessmentSubmit(BaseModel):
    """Respostas do formulário: id da pergunta → valor (single) ou lista de valores (multiple)."""

    answers: dict[str, str | list[str] | None]


class AreaScore(BaseModel):
    area: str
    title: str
    desc: str
    icon: str
    color: str
    score: float
    max_score: float
    pct: int


class AssessmentResult(BaseModel):
    id: int
    version: int
    created_at: datetime
    answers: dict[str, str | list[str]]
    top_area: str
    scores: list[AreaScore]
    recommendations: list[AreaScore]
    why: list[WhyItem]
    discipline: Discipline
    pdi: list[PdiItem]
