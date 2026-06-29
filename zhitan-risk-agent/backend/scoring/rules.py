from __future__ import annotations

from schemas.risk import RiskDimension, RiskSignal
from scoring.confidence import confidence_weight


def weighted_signal_score(signal: RiskSignal) -> float:
    return signal.baseScore * confidence_weight(signal.confidence)


def dimension_score(dimension: RiskDimension) -> float:
    return round(sum(weighted_signal_score(signal) for signal in dimension.signals), 2)


def apply_combo_bonus(dimensions: list[RiskDimension]) -> tuple[float, list[str]]:
    signals = {signal.type for dimension in dimensions for signal in dimension.signals}
    bonus = 0.0
    conflicts: list[str] = []
    if {"new_company", "zero_paid_capital", "scale_gap"}.issubset(signals):
        bonus += 2
        conflicts.append("成立时间短、实缴资本为 0 与规模差异同时出现，已按高风险组合加权。")
    if "labor_disputes" in signals and "negative_interview" in signals:
        bonus += 1
        conflicts.append("劳动争议与负面面试反馈同时出现，已提高综合风险权重。")
    if "long_posting" in signals and "high_salary" in signals:
        bonus += 1
        conflicts.append("岗位长期挂出且薪资偏高，已提高岗位风险权重。")
    return bonus, conflicts


def coverage_count(dimensions: list[RiskDimension]) -> int:
    return sum(1 for dimension in dimensions if dimension.signals or dimension.confidence in {"high", "medium"})


def high_or_medium_ratio(dimensions: list[RiskDimension]) -> float:
    all_signals = [signal for dimension in dimensions for signal in dimension.signals]
    if not all_signals:
        return 0
    qualified = [signal for signal in all_signals if signal.confidence in {"high", "medium"}]
    return len(qualified) / len(all_signals)


def has_high_confidence_critical(dimensions: list[RiskDimension]) -> bool:
    return any(signal.confidence == "high" and signal.baseScore >= 2 for dimension in dimensions for signal in dimension.signals)
