from __future__ import annotations

from core.config import AppConfig
from core.schemas import (
    AmbiguityAssessment,
    ConfidenceResult,
    DecisionResult,
    DecisionType,
    GeneratedAnswer,
    RetrievedChunk,
)


class DecisionPolicy:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def decide(
        self,
        *,
        confidence: ConfidenceResult,
        ambiguity: AmbiguityAssessment,
        answer: GeneratedAnswer,
        evidence: list[RetrievedChunk],
        answer_threshold: float | None = None,
        clarification_threshold: float | None = None,
    ) -> DecisionResult:
        answer_cutoff = answer_threshold or self.config.decision.answer_threshold
        clarification_cutoff = (
            clarification_threshold or self.config.decision.clarification_threshold
        )
        overrides: list[str] = []

        if not evidence or evidence[0].score < self.config.confidence.no_evidence_threshold:
            overrides.append("No relevant evidence was retrieved.")
            return self._abstain(overrides)

        if (
            ambiguity.is_ambiguous
            and evidence[0].score >= self.config.confidence.no_evidence_threshold
            and confidence.total_confidence < answer_cutoff
        ):
            overrides.append("Query is underspecified relative to the available evidence.")
            return self._clarify(overrides)

        if (
            answer.insufficient_evidence
            or confidence.components.insufficiency_penalty >= 0.80
        ):
            overrides.append("Retrieved evidence is too weak or sparse to support a reliable answer.")
            return self._abstain(overrides)

        if confidence.components.answer_support < self.config.decision.unsupported_answer_threshold:
            overrides.append("Generated answer is not sufficiently supported by the retrieved evidence.")
            return self._abstain(overrides)

        if ambiguity.is_ambiguous and clarification_cutoff <= confidence.total_confidence < answer_cutoff:
            overrides.append("Query is underspecified and confidence is only middling.")
            return self._clarify(overrides)

        if confidence.total_confidence >= answer_cutoff:
            return DecisionResult(
                decision=DecisionType.ANSWER,
                response_text=answer.text,
                rationale="Confidence is above the answer threshold and the response is supported by retrieved evidence.",
                override_reasons=[],
            )

        if confidence.total_confidence >= clarification_cutoff:
            overrides.append("Confidence is moderate, so clarification is safer than answering directly.")
            return self._clarify(overrides)

        overrides.append("Confidence is below the clarification threshold.")
        return self._abstain(overrides)

    @staticmethod
    def _clarify(overrides: list[str]) -> DecisionResult:
        return DecisionResult(
            decision=DecisionType.ASK_FOR_CLARIFICATION,
            response_text=(
                "Your question appears to be underspecified relative to the uploaded documents. "
                "Could you specify which topic, section, or aspect you mean?"
            ),
            rationale="The system detected ambiguity or only moderate confidence, so it requests clarification before answering.",
            override_reasons=overrides,
        )

    @staticmethod
    def _abstain(overrides: list[str]) -> DecisionResult:
        return DecisionResult(
            decision=DecisionType.ABSTAIN,
            response_text=(
                "I do not have enough reliable evidence in the uploaded documents to answer confidently."
            ),
            rationale="The system abstained because the retrieved evidence was not strong enough to support a trustworthy answer.",
            override_reasons=overrides,
        )
