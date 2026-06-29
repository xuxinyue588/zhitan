from __future__ import annotations

from datetime import datetime, timezone

from data.sample_companies import FALLBACK_CHECKLIST
from services.search_service import search_company_risks
from services.llm_service import summarize_search_results
from schemas.risk import QueryContext, RiskDimension, RiskSignal

_FETCHED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%d")

_ALL_DIMS = ["scale", "capital", "legal", "online", "position"]

_DIM_DEFAULTS: dict[str, dict] = {
    "scale": {"summary": "规模信息暂无公开数据，无法核验。", "confidence": "low"},
    "capital": {"summary": "资金信息暂无公开数据，无法核验。", "confidence": "low"},
    "legal": {"summary": "未检索到明显法律合规风险信息。", "confidence": "low"},
    "online": {"summary": "公开信息不足，无法形成稳定判断。", "confidence": "low"},
    "position": {"summary": "岗位信息暂无公开数据，无法核验。", "confidence": "low"},
}


def _build_signal(sig: dict, dim_name: str) -> RiskSignal:
    return RiskSignal(
        type=sig.get("type", f"{dim_name}_signal"),
        title=sig.get("title", "风险信号"),
        description=sig.get("description", sig.get("title", "")),
        source="网页检索摘要",
        sourceType="search",
        confidence="medium",
        fetchedAt=_FETCHED_AT,
        rawValue=None,
        baseScore=float(sig.get("baseScore", 0)),
        explanation=sig.get("description", ""),
        suggestion=sig.get("suggestion"),
    )


def _build_insufficient_signal() -> RiskSignal:
    return RiskSignal(
        type="insufficient_public_info",
        title="公开信息不足",
        description="未能通过搜索获取到足够的公开信息，建议按自检清单进一步核验。",
        source="数据不足兜底流程",
        sourceType="mock",
        confidence="low",
        fetchedAt=_FETCHED_AT,
        rawValue="搜索无结果",
        baseScore=0,
        explanation="数据覆盖不足时不输出明确负面判断。",
        suggestion="建议通过官网、面试沟通和工商信息逐项核验。",
    )


def search_risks(context: QueryContext, sample_company: dict | None) -> tuple[list[RiskDimension], list[str]]:
    warnings: list[str] = []

    # Sample company — return as-is
    if sample_company:
        return [RiskDimension.model_validate(item) for item in sample_company.get("dimensions", [])], warnings

    company_name = context.standardName or context.companyName
    search_results = search_company_risks(company_name)
    summary = summarize_search_results(company_name, search_results)
    warnings.extend(summary.get("warnings", []))

    if not search_results:
        warnings.append("未能获取到公开搜索结果，已进入数据不足流程。")
        # Return all 5 dimensions with insufficient signal on online
        dims = []
        for name in _ALL_DIMS:
            default = _DIM_DEFAULTS[name]
            signals = [_build_insufficient_signal()] if name == "online" else []
            dims.append(RiskDimension(
                name=name,
                riskScore=0,
                confidence="low",
                summary=default["summary"],
                signals=signals,
            ))
        return dims, warnings

    # Build 5 dimensions from LLM/rule output
    raw_dims: dict = summary.get("dimensions", {})
    dimensions: list[RiskDimension] = []

    for name in _ALL_DIMS:
        raw = raw_dims.get(name, {})
        default = _DIM_DEFAULTS[name]
        confidence = raw.get("confidence", default["confidence"])
        summary_text = raw.get("summary", default["summary"])
        signals = [_build_signal(s, name) for s in raw.get("signals", [])]
        risk_score = round(sum(s.baseScore for s in signals), 2)
        dimensions.append(RiskDimension(
            name=name,
            riskScore=risk_score,
            confidence=confidence,
            summary=summary_text,
            signals=signals,
        ))

    return dimensions, warnings


def fallback_checklist() -> list[str]:
    return list(FALLBACK_CHECKLIST)
