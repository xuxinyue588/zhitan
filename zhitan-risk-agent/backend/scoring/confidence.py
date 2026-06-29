from __future__ import annotations

WEIGHTS = {"high": 1.0, "medium": 0.7, "low": 0.5}


def confidence_weight(confidence: str) -> float:
    return WEIGHTS.get(confidence, 0.5)
