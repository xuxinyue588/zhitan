from __future__ import annotations

from uuid import uuid4
from datetime import datetime, timezone

from schemas.risk import QueryContext, QueryRequest, PositionInfo


def parse_query(request: QueryRequest) -> QueryContext:
    raw_query = request.query.strip()
    query_type = request.queryType
    if query_type is None:
        if raw_query.lower().startswith(("http://", "https://")) or ".com" in raw_query:
            query_type = "job_link"
        else:
            query_type = "company_name"

    company_name = raw_query
    position_info = request.positionInfo

    if query_type == "job_link":
        company_name = extract_company_from_text(raw_query)
        if position_info is None:
            position_info = PositionInfo(title="岗位链接解析中", salary=None, stage=None, scale=None)

    return QueryContext(
        queryId=str(uuid4()),
        queryType=query_type,
        companyName=company_name,
        positionInfo=position_info,
        createdAt=datetime.now(timezone.utc).isoformat(),
    )


def extract_company_from_text(text: str) -> str:
    known_markers = ["公司=", "company=", "公司：", "公司:"]
    for marker in known_markers:
        if marker in text:
            tail = text.split(marker, 1)[1]
            return tail.split("&", 1)[0].split(" ", 1)[0].strip() or text
    return text.strip()
