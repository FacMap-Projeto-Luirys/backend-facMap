"""
Cálculo do resultado da avaliação a partir de app/data/assessment.json.

Regras:
- Cada opção marcada soma os seus `weights` na pontuação de cada área.
- A pontuação máxima de uma área é o que ela faria se o aluno respondesse sempre a
  favor dela (maior peso nas perguntas `single`, soma dos pesos nas `multiple`).
- Afinidade (%) = base_pct + (100 - base_pct) * pontuação / máximo.
- Recomendações = as `top_n` áreas com maior afinidade (empate: ordem do JSON).
- "Por que esse resultado", disciplina e PDI vêm de `results` da área com maior afinidade.

Para mudar perguntas, pesos ou textos basta editar o JSON: ele é relido quando muda,
sem precisar reiniciar o servidor.
"""

import json
from pathlib import Path

from app.schemas.assessment import AreaScore, AssessmentConfig, FormResponse

CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "assessment.json"

_cache: tuple[float, AssessmentConfig] | None = None

Answers = dict[str, str | list[str]]


class AnswerError(ValueError):
    pass


def load_config() -> AssessmentConfig:
    """Lê e valida o JSON; recarrega automaticamente quando o arquivo é alterado."""
    global _cache
    mtime = CONFIG_PATH.stat().st_mtime
    if _cache is None or _cache[0] != mtime:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        _cache = (mtime, AssessmentConfig.model_validate(data))
    return _cache[1]


def public_form(config: AssessmentConfig) -> FormResponse:
    """Formulário sem os pesos (o frontend não precisa deles)."""
    return FormResponse.model_validate(config.model_dump())


def normalize_answers(config: AssessmentConfig, raw: dict[str, str | list[str] | None]) -> Answers:
    """Valida as respostas contra o JSON e devolve um dicionário limpo."""
    questions = {q.id for q in config.questions}
    if unknown := set(raw) - questions:
        raise AnswerError(f"Perguntas desconhecidas: {sorted(unknown)}")

    clean: Answers = {}
    for q in config.questions:
        value = raw.get(q.id)
        valid = {o.value: o for o in q.options}

        if q.type == "single":
            if value in (None, ""):
                if q.required:
                    raise AnswerError(f"Responda a pergunta '{q.label}'.")
                continue
            if not isinstance(value, str) or value not in valid:
                raise AnswerError(f"Resposta inválida para '{q.label}': {value!r}")
            clean[q.id] = value
        else:
            if value is None:
                values: list[str] = []
            elif isinstance(value, str):
                values = [value]
            else:
                values = list(dict.fromkeys(value))  # remove duplicadas mantendo a ordem
            if not values:
                if q.required:
                    raise AnswerError(f"Marque ao menos uma opção em '{q.label}'.")
                continue
            if bad := [v for v in values if v not in valid]:
                raise AnswerError(f"Opções inválidas para '{q.label}': {bad}")
            if len(values) > 1 and any(valid[v].exclusive for v in values):
                raise AnswerError(f"Em '{q.label}', a opção exclusiva não pode ser combinada com outras.")
            clean[q.id] = values
    return clean


def _max_scores(config: AssessmentConfig) -> dict[str, float]:
    maxes = {area: 0.0 for area in config.areas}
    for q in config.questions:
        for area in config.areas:
            weights = [max(o.weights.get(area, 0), 0) for o in q.options]
            maxes[area] += sum(weights) if q.type == "multiple" else max(weights)
    return maxes


def compute_result(config: AssessmentConfig, answers: Answers) -> dict:
    """Calcula as pontuações e monta o resultado (id e data vêm do banco)."""
    scores = {area: 0.0 for area in config.areas}
    for q in config.questions:
        chosen = answers.get(q.id)
        if chosen is None:
            continue
        chosen_set = {chosen} if isinstance(chosen, str) else set(chosen)
        for opt in q.options:
            if opt.value in chosen_set:
                for area, w in opt.weights.items():
                    scores[area] += w

    maxes = _max_scores(config)
    base = config.scoring.base_pct
    order = list(config.areas)

    area_scores: list[AreaScore] = []
    for area, cfg in config.areas.items():
        ratio = scores[area] / maxes[area] if maxes[area] > 0 else 0.0
        pct = round(base + (100 - base) * min(max(ratio, 0.0), 1.0))
        area_scores.append(
            AreaScore(
                area=area,
                title=cfg.title,
                desc=cfg.desc,
                icon=cfg.icon,
                color=cfg.color,
                score=scores[area],
                max_score=maxes[area],
                pct=pct,
            )
        )
    area_scores.sort(key=lambda s: (-s.pct, -s.score, order.index(s.area)))

    top = area_scores[0].area
    details = config.results[top]
    return {
        "version": config.version,
        "answers": answers,
        "top_area": top,
        "scores": [s.model_dump() for s in area_scores],
        "recommendations": [s.model_dump() for s in area_scores[: config.scoring.top_n]],
        "why": [w.model_dump() for w in details.why],
        "discipline": details.discipline.model_dump(),
        "pdi": [p.model_dump() for p in details.pdi],
    }
