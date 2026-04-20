from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DecisionType(str, Enum):
    ANSWER = "ANSWER"
    ASK_FOR_CLARIFICATION = "ASK_FOR_CLARIFICATION"
    ABSTAIN = "ABSTAIN"


class LoadedDocument(BaseModel):
    file_name: str
    text: str
    page_number: int | None = None


class DocumentChunk(BaseModel):
    chunk_id: str
    file_name: str
    text: str
    page_number: int | None = None
    chunk_index: int


class RetrievedChunk(BaseModel):
    chunk_id: str
    file_name: str
    page_number: int | None = None
    text: str
    score: float
    rank: int


class GeneratedAnswer(BaseModel):
    text: str
    citations: list[str] = Field(default_factory=list)
    generator_mode: str = "fallback"
    grounded: bool = True
    insufficient_evidence: bool = False


class AmbiguityAssessment(BaseModel):
    is_ambiguous: bool
    score: float
    reasons: list[str] = Field(default_factory=list)


class ConfidenceComponents(BaseModel):
    retrieval_relevance: float
    evidence_coverage: float
    answer_support: float
    ambiguity_penalty: float
    insufficiency_penalty: float


class ConfidenceResult(BaseModel):
    total_confidence: float
    components: ConfidenceComponents
    rationale: list[str] = Field(default_factory=list)


class DecisionResult(BaseModel):
    decision: DecisionType
    response_text: str
    rationale: str
    override_reasons: list[str] = Field(default_factory=list)


class QueryResult(BaseModel):
    query: str
    ambiguity: AmbiguityAssessment
    answer: GeneratedAnswer
    confidence: ConfidenceResult
    decision: DecisionResult
    evidence: list[RetrievedChunk]


class IndexBuildResult(BaseModel):
    index_name: str
    index_path: str
    metadata_path: str
    document_count: int
    chunk_count: int
    file_names: list[str]
    ingestion_errors: list[str] = Field(default_factory=list)


class LogEntry(BaseModel):
    timestamp: str
    query: str
    decision: str
    confidence: float
    component_scores: dict[str, float]
    retrieved_sources: list[dict[str, Any]]
    generated_response: str
    rationale: str


class EvalExample(BaseModel):
    query: str
    expected_decision: DecisionType
    gold_answer_category: str | None = None
    notes: str | None = None

    model_config = ConfigDict(use_enum_values=False)
