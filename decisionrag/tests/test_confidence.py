from core.config import get_config
from core.schemas import AmbiguityAssessment, GeneratedAnswer, RetrievedChunk
from uncertainty.confidence import ConfidenceEstimator


def test_confidence_is_high_for_supported_answer() -> None:
    estimator = ConfidenceEstimator(get_config())
    evidence = [
        RetrievedChunk(
            chunk_id="memo-1",
            file_name="technical_memo.md",
            page_number=None,
            text="The system may recommend an answer only when confidence is at least 0.80 and two passages exceed 0.60 similarity.",
            score=0.91,
            rank=1,
        ),
        RetrievedChunk(
            chunk_id="memo-2",
            file_name="technical_memo.md",
            page_number=None,
            text="Questions with vague references trigger an ambiguity flag and clarification.",
            score=0.81,
            rank=2,
        ),
    ]
    answer = GeneratedAnswer(
        text="The technical memo says the system can recommend an answer only when confidence reaches at least 0.80 and two retrieved passages exceed 0.60 similarity.",
        citations=["memo-1", "memo-2"],
    )
    ambiguity = AmbiguityAssessment(is_ambiguous=False, score=0.0, reasons=[])
    result = estimator.estimate("What deployment requirement is needed?", evidence, answer, ambiguity)
    assert result.total_confidence > 0.75


def test_confidence_drops_with_weak_evidence() -> None:
    estimator = ConfidenceEstimator(get_config())
    evidence = [
        RetrievedChunk(
            chunk_id="weak-1",
            file_name="policy_note.txt",
            page_number=None,
            text="The board prefers documented evidence.",
            score=0.42,
            rank=1,
        )
    ]
    answer = GeneratedAnswer(
        text="The retrieved evidence is insufficient to support a reliable answer.",
        citations=[],
        insufficient_evidence=True,
    )
    ambiguity = AmbiguityAssessment(is_ambiguous=True, score=0.65, reasons=["very short query"])
    result = estimator.estimate("What about it?", evidence, answer, ambiguity)
    assert result.total_confidence < 0.45
