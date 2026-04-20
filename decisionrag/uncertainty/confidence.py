from __future__ import annotations

from core.config import AppConfig
from core.schemas import (
    AmbiguityAssessment,
    ConfidenceComponents,
    ConfidenceResult,
    GeneratedAnswer,
    RetrievedChunk,
)
from uncertainty.signals import (
    compute_answer_support,
    compute_evidence_coverage,
    compute_insufficiency_penalty,
    compute_retrieval_relevance,
)


class ConfidenceEstimator:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def estimate(
        self,
        query: str,
        evidence: list[RetrievedChunk],
        answer: GeneratedAnswer,
        ambiguity: AmbiguityAssessment,
    ) -> ConfidenceResult:
        retrieval_relevance = compute_retrieval_relevance(evidence)
        evidence_coverage = compute_evidence_coverage(
            evidence,
            relevance_threshold=self.config.retrieval.relevance_threshold,
        )
        answer_support = compute_answer_support(query, answer, evidence)
        ambiguity_penalty = ambiguity.score if ambiguity.is_ambiguous else 0.0
        insufficiency_penalty = compute_insufficiency_penalty(
            query,
            evidence,
            relevance_threshold=self.config.retrieval.relevance_threshold,
            min_supporting_chunks=self.config.retrieval.min_supporting_chunks,
        )

        total_confidence = _clip(
            (0.50 * retrieval_relevance)
            + (0.20 * evidence_coverage)
            + (0.35 * answer_support)
            - (0.15 * ambiguity_penalty)
            - (0.15 * insufficiency_penalty)
        )
        components = ConfidenceComponents(
            retrieval_relevance=retrieval_relevance,
            evidence_coverage=evidence_coverage,
            answer_support=answer_support,
            ambiguity_penalty=ambiguity_penalty,
            insufficiency_penalty=insufficiency_penalty,
        )
        rationale = self._build_rationale(components, ambiguity)
        return ConfidenceResult(
            total_confidence=total_confidence,
            components=components,
            rationale=rationale,
        )

    @staticmethod
    def _build_rationale(
        components: ConfidenceComponents,
        ambiguity: AmbiguityAssessment,
    ) -> list[str]:
        rationale = [
            f"Retrieval relevance is {components.retrieval_relevance:.2f} based on the top evidence scores.",
            f"Evidence coverage is {components.evidence_coverage:.2f} based on how many retrieved chunks clear the relevance threshold.",
            f"Answer support is {components.answer_support:.2f} from lexical overlap between the response and retrieved evidence.",
        ]
        if ambiguity.is_ambiguous:
            rationale.append(
                f"Ambiguity penalty is {components.ambiguity_penalty:.2f} because the query is underspecified: {', '.join(ambiguity.reasons)}."
            )
        rationale.append(
            f"Insufficiency penalty is {components.insufficiency_penalty:.2f}; higher values indicate thinner or weaker evidence."
        )
        return rationale


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
