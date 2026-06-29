from __future__ import annotations

from agents.entity_agent import normalize_entity
from agents.parser_agent import parse_query
from agents.risk_search_agent import fallback_checklist, search_risks
from agents.risk_judge_agent import judge_risks
from agents.report_gen_agent import generate_report_summary
from agents.qa_agent import generate_questions
from agents.quality_agent import inspect_quality
from agents.render_agent import render_report
from data.sample_companies import DEFAULT_FEEDBACK, DISCLAIMER, FEEDBACK, now_iso
from schemas.risk import QueryRequest, RiskReport


def run_pipeline(request: QueryRequest) -> RiskReport:
    context = parse_query(request)
    context, sample_company = normalize_entity(context)
    dimensions, warnings = search_risks(context, sample_company)
    verdict = judge_risks(dimensions)
    verdict = generate_report_summary(verdict, dimensions)
    questions = generate_questions(verdict.topSignals)
    feedback = FEEDBACK.get(context.standardName or context.companyName, DEFAULT_FEEDBACK)
    checklist = fallback_checklist()
    quality = inspect_quality(verdict, dimensions, questions, warnings)

    report = RiskReport(
        queryContext=context,
        verdict=verdict,
        dimensions=dimensions,
        interviewQuestions=questions,
        feedback=feedback,
        fallbackChecklist=checklist,
        quality=quality,
        disclaimer=DISCLAIMER,
        generatedAt=now_iso(),
    )
    return render_report(report)
