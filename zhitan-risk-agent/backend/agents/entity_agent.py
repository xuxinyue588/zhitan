from __future__ import annotations

from copy import deepcopy

from data.sample_companies import SAMPLE_COMPANIES
from schemas.risk import QueryContext


def normalize_entity(context: QueryContext) -> tuple[QueryContext, dict | None]:
    query = context.companyName.strip()
    for name, company in SAMPLE_COMPANIES.items():
        aliases = company.get("aliases", [])
        if query == name or query in aliases or name in query:
            updated = context.model_copy(deep=True)
            updated.companyName = query
            updated.standardName = name
            updated.creditCode = company.get("creditCode")
            updated.aliases = list(aliases)
            if updated.positionInfo is None and company.get("positionInfo"):
                updated.positionInfo = company.get("positionInfo")
            return updated, deepcopy(company)

    updated = context.model_copy(deep=True)
    updated.standardName = query
    updated.aliases = []
    return updated, None
