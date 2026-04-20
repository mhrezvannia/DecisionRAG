from __future__ import annotations

import re

from core.config import AppConfig
from core.schemas import AmbiguityAssessment


VAGUE_PATTERNS = (
    r"^what about",
    r"^what happened",
    r"^what does it say",
    r"^explain this",
    r"^what about the result",
    r"^what about the review",
)

VAGUE_TERMS = {"this", "that", "it", "result", "review", "thing", "stuff", "part", "section"}


class AmbiguityDetector:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def assess(self, query: str) -> AmbiguityAssessment:
        normalized = query.strip().lower()
        reasons: list[str] = []
        score = 0.0

        if len(normalized.split()) <= 3:
            score += 0.35
            reasons.append("very short query")

        if any(re.search(pattern, normalized) for pattern in VAGUE_PATTERNS):
            score += 0.40
            reasons.append("matches vague query pattern")

        vague_hits = [term for term in VAGUE_TERMS if re.search(rf"\b{term}\b", normalized)]
        if vague_hits:
            score += 0.25
            reasons.append(f"contains vague references ({', '.join(sorted(vague_hits))})")

        if "?" not in query and len(normalized.split()) <= 5:
            score += 0.10
            reasons.append("lacks detail")

        final_score = min(score, 1.0)
        return AmbiguityAssessment(
            is_ambiguous=final_score >= self.config.confidence.ambiguity_score_threshold,
            score=final_score,
            reasons=reasons,
        )
