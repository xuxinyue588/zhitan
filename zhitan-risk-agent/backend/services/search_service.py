from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

import httpx

_EXA_API = "https://api.exa.ai/search"
_EXA_TIMEOUT = 20


def _exa_search(query: str, num_results: int = 5) -> list[dict]:
    """Search via Exa REST API directly."""
    api_key = os.environ.get("EXA_API_KEY", "")
    if not api_key:
        return []
    try:
        resp = httpx.post(
            _EXA_API,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json={
                "query": query,
                "numResults": num_results,
                "type": "neural",
                "contents": {"text": {"maxCharacters": 2000}},
            },
            timeout=_EXA_TIMEOUT,
        )
        if resp.status_code != 200:
            return []
        results = resp.json().get("results", [])
        return [
            {
                "url": r.get("url", ""),
                "title": r.get("title", ""),
                "snippet": r.get("text", ""),
                "source": "exa",
            }
            for r in results
            if r.get("text")
        ]
    except Exception:
        return []


def search_company_risks(company_name: str) -> list[dict]:
    """Search company risk info via Exa API (parallel queries across dimensions)."""
    queries = [
        f"{company_name} 员工评价 工作体验 裁员",
        f"{company_name} 劳动纠纷 投诉 行政处罚",
        f"{company_name} 公司规模 融资 上市",
        f"{company_name} 招聘 岗位 JD",
    ]

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(_exa_search, q, 3) for q in queries]
        for f in as_completed(futures):
            results.extend(f.result())

    return results
