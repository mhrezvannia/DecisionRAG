from core.config import get_config
from decision.ambiguity import AmbiguityDetector


def test_detects_vague_query_pattern() -> None:
    detector = AmbiguityDetector(get_config())
    assessment = detector.assess("Explain this result.")
    assert assessment.is_ambiguous is True
    assert assessment.score >= 0.55


def test_specific_query_is_not_ambiguous() -> None:
    detector = AmbiguityDetector(get_config())
    assessment = detector.assess("Which team led the pilot described in the report?")
    assert assessment.is_ambiguous is False
