from core.config import get_config
from core.schemas import (
    AmbiguityAssessment,
    ConfidenceComponents,
    ConfidenceResult,
    DecisionType,
    GeneratedAnswer,
    RetrievedChunk,
)
from decision.policy import DecisionPolicy


def test_answers_when_confidence_is_high() -> None:
    policy = DecisionPolicy(get_config())
    result = policy.decide(
        confidence=ConfidenceResult(
            total_confidence=0.82,
            components=ConfidenceComponents(
                retrieval_relevance=0.85,
                evidence_coverage=0.75,
                answer_support=0.90,
                ambiguity_penalty=0.0,
                insufficiency_penalty=0.15,
            ),
            rationale=[],
        ),
        ambiguity=AmbiguityAssessment(is_ambiguous=False, score=0.0, reasons=[]),
        answer=GeneratedAnswer(text="Supported answer.", citations=["c1"]),
        evidence=[
            RetrievedChunk(
                chunk_id="c1",
                file_name="report.md",
                page_number=None,
                text="Supported evidence.",
                score=0.88,
                rank=1,
            )
        ],
    )
    assert result.decision == DecisionType.ANSWER


def test_requests_clarification_for_ambiguous_middling_query() -> None:
    policy = DecisionPolicy(get_config())
    result = policy.decide(
        confidence=ConfidenceResult(
            total_confidence=0.57,
            components=ConfidenceComponents(
                retrieval_relevance=0.62,
                evidence_coverage=0.50,
                answer_support=0.55,
                ambiguity_penalty=0.65,
                insufficiency_penalty=0.30,
            ),
            rationale=[],
        ),
        ambiguity=AmbiguityAssessment(
            is_ambiguous=True,
            score=0.65,
            reasons=["matches vague query pattern"],
        ),
        answer=GeneratedAnswer(text="Tentative answer.", citations=["c1"]),
        evidence=[
            RetrievedChunk(
                chunk_id="c1",
                file_name="report.md",
                page_number=None,
                text="Evidence for a partially specified question.",
                score=0.70,
                rank=1,
            )
        ],
    )
    assert result.decision == DecisionType.ASK_FOR_CLARIFICATION


def test_abstains_when_answer_is_unsupported() -> None:
    policy = DecisionPolicy(get_config())
    result = policy.decide(
        confidence=ConfidenceResult(
            total_confidence=0.62,
            components=ConfidenceComponents(
                retrieval_relevance=0.76,
                evidence_coverage=0.50,
                answer_support=0.10,
                ambiguity_penalty=0.0,
                insufficiency_penalty=0.25,
            ),
            rationale=[],
        ),
        ambiguity=AmbiguityAssessment(is_ambiguous=False, score=0.0, reasons=[]),
        answer=GeneratedAnswer(text="Unsupported answer.", citations=[]),
        evidence=[
            RetrievedChunk(
                chunk_id="c1",
                file_name="policy_note.txt",
                page_number=None,
                text="Only loosely related evidence.",
                score=0.74,
                rank=1,
            )
        ],
    )
    assert result.decision == DecisionType.ABSTAIN
