from __future__ import annotations

import re

from core.schemas import GeneratedAnswer, RetrievedChunk


STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "have",
    "what",
    "about",
    "does",
    "your",
    "which",
    "into",
    "when",
    "were",
    "there",
    "their",
}


def compute_retrieval_relevance(evidence: list[RetrievedChunk]) -> float:
    if not evidence:
        return 0.0
    weights = [1.0 / hit.rank for hit in evidence]
    weighted_sum = sum(hit.score * weight for hit, weight in zip(evidence, weights))
    return _clip(weighted_sum / sum(weights))


def compute_evidence_coverage(
    evidence: list[RetrievedChunk],
    *,
    relevance_threshold: float,
) -> float:
    if not evidence:
        return 0.0
    supporting = sum(1 for hit in evidence if hit.score >= relevance_threshold)
    return _clip(supporting / len(evidence))


def compute_answer_support(
    query: str,
    answer: GeneratedAnswer,
    evidence: list[RetrievedChunk],
) -> float:
    if answer.insufficient_evidence or not answer.text.strip() or not evidence:
        return 0.0
    answer_tokens = _content_tokens(answer.text)
    evidence_tokens = set().union(*(_content_tokens(hit.text) for hit in evidence))
    query_tokens = _content_tokens(query)
    if not answer_tokens:
        return 0.0
    lexical_overlap = len(answer_tokens & evidence_tokens) / len(answer_tokens)
    query_coverage = (
        len(query_tokens & evidence_tokens) / len(query_tokens)
        if query_tokens
        else 0.0
    )
    citation_bonus = min(len(answer.citations), 3) / 3 if answer.citations else 0.0
    return _clip(
        (0.55 * lexical_overlap) + (0.20 * citation_bonus) + (0.25 * query_coverage)
    )


def compute_insufficiency_penalty(
    query: str,
    evidence: list[RetrievedChunk],
    *,
    relevance_threshold: float,
    min_supporting_chunks: int,
) -> float:
    if not evidence:
        return 1.0
    top_score = evidence[0].score
    supporting = sum(1 for hit in evidence if hit.score >= relevance_threshold)
    support_ratio = min(supporting / max(min_supporting_chunks, 1), 1.0)
    strength = (0.65 * top_score) + (0.35 * support_ratio)
    if len(evidence) < min_supporting_chunks:
        strength -= 0.10
    return _clip(1.0 - strength)


def _content_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[A-Za-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
