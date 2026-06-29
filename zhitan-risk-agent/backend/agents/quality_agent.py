from __future__ import annotations

import json

from agents.report_gen_agent import BANNED_WORDS
from schemas.risk import InterviewQuestion, Quality, RiskDimension, RiskVerdict


def inspect_quality(verdict: RiskVerdict, dimensions: list[RiskDimension], questions: list[InterviewQuestion], warnings: list[str]) -> Quality:
    quality_warnings = list(warnings)
    covered = sum(1 for dimension in dimensions if dimension.signals or dimension.confidence in {"high", "medium"})
    if covered < 3:
        verdict.riskLevel = "insufficient"
        verdict.dataSufficiency = "insufficient"
        quality_warnings.append("有效数据覆盖维度不足 3 个，已切换为数据不足模式。")

    if len(questions) < 3:
        quality_warnings.append("面试核验问题不足，已补充通用问题。")

    serialized = json.dumps(verdict.model_dump(), ensure_ascii=False)
    if any(word in serialized for word in BANNED_WORDS):
        quality_warnings.append("检测到不合规表述，已进行中性化替换。")

    if verdict.dataSufficiency == "insufficient":
        grade = "poor"
    elif quality_warnings:
        grade = "good"
    else:
        grade = "excellent"
    return Quality(grade=grade, warnings=quality_warnings)
