from __future__ import annotations

from scoring.rules import apply_combo_bonus, coverage_count, dimension_score, has_high_confidence_critical, high_or_medium_ratio
from schemas.risk import RiskConflict, RiskDimension, RiskVerdict, TopSignal


def judge_risks(dimensions: list[RiskDimension]) -> RiskVerdict:
    for dimension in dimensions:
        dimension.riskScore = dimension_score(dimension)

    bonus, conflict_descriptions = apply_combo_bonus(dimensions)
    total = round(sum(dimension.riskScore for dimension in dimensions) + bonus, 2)
    coverage = coverage_count(dimensions)
    confidence_ratio = high_or_medium_ratio(dimensions)

    if coverage < 3:
        level = "insufficient"
        sufficiency = "insufficient"
    elif total <= 2:
        level = "low"
        sufficiency = "sufficient"
    elif total <= 5 and confidence_ratio >= 0.6:
        level = "medium"
        sufficiency = "sufficient"
    elif total >= 6 and confidence_ratio >= 0.7 and has_high_confidence_critical(dimensions):
        level = "high"
        sufficiency = "sufficient"
    else:
        level = "medium"
        sufficiency = "partial"

    top_signals = build_top_signals(dimensions)
    conflicts = [RiskConflict(dimensions=["multiple"], description=item) for item in conflict_descriptions]
    return RiskVerdict(
        overallScore=total,
        riskLevel=level,
        dataSufficiency=sufficiency,
        topSignals=top_signals,
        conflicts=conflicts,
        summary=summary_for_level(level),
    )


def build_top_signals(dimensions: list[RiskDimension]) -> list[TopSignal]:
    signals = [signal for dimension in dimensions for signal in dimension.signals if signal.baseScore > 0 or signal.type == "insufficient_public_info"]
    signals.sort(key=lambda item: item.baseScore, reverse=True)
    result: list[TopSignal] = []
    for signal in signals[:6]:
        severity = "critical" if signal.baseScore >= 3 else "warning" if signal.baseScore > 0 else "info"
        result.append(
            TopSignal(
                signal=signal.title,
                severity=severity,
                explanation=signal.explanation or signal.description,
                source=signal.source,
                confidence=signal.confidence,
                suggestion=signal.suggestion,
            )
        )
    return result


def summary_for_level(level: str) -> str:
    return {
        "low": "公开信息整体正常，可进一步了解。",
        "medium": "存在部分风险信号，建议在沟通中重点核验。",
        "high": "存在多项组织稳定性或信息透明度风险信号，请谨慎评估投入时间。",
        "insufficient": "该公司公开信息较少，建议结合自检清单和面试沟通进一步核验。",
    }[level]
