from __future__ import annotations

from schemas.risk import RiskDimension, RiskVerdict

BANNED_WORDS = ["垃圾公司", "骗子公司", "皮包公司", "千万别去", "不值得投"]


def generate_report_summary(verdict: RiskVerdict, dimensions: list[RiskDimension]) -> RiskVerdict:
    if not verdict.topSignals:
        verdict.summary = sanitize(verdict.summary)
        return verdict

    leading = verdict.topSignals[0]
    if verdict.riskLevel == "low":
        verdict.summary = "公开信息整体正常，暂未发现明显影响投递判断的风险信号。"
    elif verdict.riskLevel == "insufficient":
        verdict.summary = "公开信息覆盖不足，当前更适合通过自检清单和面试问题继续核验。"
    else:
        verdict.summary = f"主要风险集中在“{leading.signal}”，建议围绕该点优先核验。"

    verdict.summary = sanitize(verdict.summary)
    for signal in verdict.topSignals:
        signal.explanation = sanitize(signal.explanation)
        if signal.suggestion:
            signal.suggestion = sanitize(signal.suggestion)
    return verdict


def sanitize(text: str) -> str:
    cleaned = text
    for word in BANNED_WORDS:
        cleaned = cleaned.replace(word, "存在风险信号，建议核验")
    return cleaned
