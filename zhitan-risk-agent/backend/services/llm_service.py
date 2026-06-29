from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

import httpx

_DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"
_MODEL = "deepseek-chat"
_TIMEOUT = 30
_FETCHED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%d")

_DIMENSION_NAMES = ["scale", "capital", "legal", "online", "position"]

_SYSTEM_PROMPT = """\
你是一个专业的求职风险分析助手。根据用户提供的公司相关网页文本，分析该公司在5个维度的风险，输出 JSON。

维度说明：
- scale: 公司规模真实性（招聘规模与实际人数是否匹配）
- capital: 资金/融资稳定性（注册资本、实缴、融资情况）
- legal: 法律合规（劳动争议、行政处罚、诉讼记录）
- online: 网络透明度（官网质量、公开反馈、员工评价）
- position: 岗位真实性（JD质量、薪资异常、长期挂岗等）

严格规则：
1. 只输出搜索文本中有明确依据的信号，禁止编造或推测
2. 信息不足时，该维度 confidence 必须设为 "low"，signals 设为空数组
3. 正面信息（公司好的一面）不是风险信号，不要输出 baseScore=0 的正面描述
4. signals 只记录风险信号（baseScore>0），或有助于求职者核验的注意点

baseScore 规则：1=轻微需关注，2=中等风险，3=严重风险
confidence: high=文本中有直接证据, medium=有间接线索, low=文本中无相关信息

输出格式（严格 JSON，不要有 markdown 代码块）：
{
  "scale": {"summary": "一句话说明，信息不足时写'搜索文本未涉及规模信息'", "confidence": "low|medium|high", "signals": []},
  "capital": {"summary": "...", "confidence": "low|medium|high", "signals": []},
  "legal": {"summary": "...", "confidence": "low|medium|high", "signals": []},
  "online": {"summary": "...", "confidence": "low|medium|high", "signals": []},
  "position": {"summary": "...", "confidence": "low|medium|high", "signals": []}
}

signals 中每项格式：{"type": "snake_case类型", "title": "简短标题", "description": "具体描述（引用原文）", "baseScore": 1.0, "suggestion": "建议核验方式"}"""


# ---------------------------------------------------------------------------
# Keyword-based fallback
# ---------------------------------------------------------------------------

_KEYWORD_RULES: list[tuple[str, str, str, str, float, str]] = [
    # (keyword, dim, type, title, score, suggestion)
    ("裁员", "online", "layoff_discussion", "组织调整讨论", 2, "建议确认所在业务线是否稳定。"),
    ("优化", "online", "layoff_discussion", "组织调整讨论", 1, "建议确认团队近期是否有变化。"),
    ("劳动仲裁", "legal", "labor_disputes", "劳动争议记录", 3, "建议面试中确认绩效和劳动合同条款。"),
    ("劳动争议", "legal", "labor_disputes", "劳动争议记录", 2, "建议确认离职交接和绩效规则。"),
    ("行政处罚", "legal", "administrative_penalty", "行政处罚记录", 2, "建议了解公司合规情况。"),
    ("工资拖欠", "legal", "wage_delay", "工资拖欠风险", 3, "建议确认薪资发放记录和发薪日。"),
    ("融资", "capital", "funding_mentioned", "融资信息提及", 0, "建议核实融资主体和投资方。"),
    ("注册资本", "capital", "capital_info", "注册资本信息", 0, "可进一步核实实缴情况。"),
    ("骗局", "online", "scam_signal", "负面评价信号", 3, "建议谨慎核验，通过面试充分了解。"),
    ("差评", "online", "negative_feedback", "负面反馈信号", 2, "建议结合面试沟通综合判断。"),
    ("官网", "online", "website_check", "官网信息", 0, "可访问官网核验业务真实性。"),
    ("人员变动", "scale", "staff_turnover", "人员变动信号", 1, "建议确认团队稳定性。"),
]


def _rule_based_extract(company_name: str, search_results: list[dict]) -> dict:
    full_text = " ".join(r.get("snippet", "") for r in search_results)
    dims: dict[str, dict] = {
        name: {"summary": "公开信息有限，无法形成明确判断。", "confidence": "low", "signals": []}
        for name in _DIMENSION_NAMES
    }
    seen: set[str] = set()
    for keyword, dim, sig_type, title, score, suggestion in _KEYWORD_RULES:
        if keyword in full_text and sig_type not in seen:
            seen.add(sig_type)
            dims[dim]["confidence"] = "medium"
            dims[dim]["summary"] = f"检测到关键词「{keyword}」，建议进一步核验。"
            dims[dim]["signals"].append({
                "type": sig_type,
                "title": title,
                "description": f"在搜索结果中检测到「{keyword}」相关内容。",
                "baseScore": score,
                "suggestion": suggestion,
            })
    return dims


# ---------------------------------------------------------------------------
# LLM extraction
# ---------------------------------------------------------------------------

def _llm_extract(company_name: str, search_results: list[dict]) -> dict | None:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return None

    snippets = "\n\n".join(
        f"[{i+1}] {r.get('title','')}\n{r.get('snippet','')[:1500]}"
        for i, r in enumerate(search_results[:6])
    )
    user_msg = f"公司名称：{company_name}\n\n搜索结果摘要：\n{snippets}"

    try:
        resp = httpx.post(
            _DEEPSEEK_API,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": _MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
            timeout=_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        content = resp.json()["choices"][0]["message"]["content"]
        # strip potential markdown fences
        content = re.sub(r"```json\s*|```\s*", "", content).strip()
        return json.loads(content)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def summarize_search_results(company_name: str, search_results: list[dict]) -> dict:
    if not search_results:
        return {"signals": [], "warnings": ["搜索 API 未配置，已跳过网页检索。"]}

    dims = _llm_extract(company_name, search_results)
    if dims is None:
        dims = _rule_based_extract(company_name, search_results)

    return {"signals": [], "warnings": [], "dimensions": dims}
