from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class PathConfig:
    project_root: Path
    indices_dir: Path
    logs_dir: Path
    sample_docs_dir: Path


@dataclass(frozen=True)
class ChunkingConfig:
    target_chunk_chars: int = 650
    overlap_chars: int = 120
    min_chunk_chars: int = 220


@dataclass(frozen=True)
class RetrievalConfig:
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 4
    relevance_threshold: float = 0.60
    min_supporting_chunks: int = 2


@dataclass(frozen=True)
class ProviderConfig:
    api_key: str | None
    base_url: str | None
    model_name: str


@dataclass(frozen=True)
class LLMConfig:
    default_provider: str
    openai: ProviderConfig
    gemini: ProviderConfig
    llama: ProviderConfig
    temperature: float = 0.0


@dataclass(frozen=True)
class ConfidenceConfig:
    ambiguity_score_threshold: float = 0.55
    no_evidence_threshold: float = 0.45


@dataclass(frozen=True)
class DecisionConfig:
    answer_threshold: float = 0.75
    clarification_threshold: float = 0.45
    unsupported_answer_threshold: float = 0.25


@dataclass(frozen=True)
class AppConfig:
    paths: PathConfig
    chunking: ChunkingConfig
    retrieval: RetrievalConfig
    llm: LLMConfig
    confidence: ConfidenceConfig
    decision: DecisionConfig


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    load_dotenv()
    project_root = Path(__file__).resolve().parents[1]
    paths = PathConfig(
        project_root=project_root,
        indices_dir=project_root / "storage" / "indices",
        logs_dir=project_root / "storage" / "logs",
        sample_docs_dir=project_root / "data" / "sample_docs",
    )
    llm = LLMConfig(
        default_provider=os.getenv("DEFAULT_LLM_PROVIDER", "gemini"),
        openai=ProviderConfig(
            api_key=os.getenv("OPENAI_API_KEY") or None,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            model_name=os.getenv("OPENAI_MODEL", os.getenv("LLM_MODEL", "gpt-4o-mini")),
        ),
        gemini=ProviderConfig(
            api_key=os.getenv("GEMINI_API_KEY") or None,
            base_url=os.getenv(
                "GEMINI_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai/",
            ),
            model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        ),
        llama=ProviderConfig(
            api_key=os.getenv("LLAMA_API_KEY") or None,
            base_url=os.getenv("LLAMA_BASE_URL", "http://localhost:11434/v1"),
            model_name=os.getenv("LLAMA_MODEL", "llama3.1:8b"),
        ),
    )
    retrieval = RetrievalConfig(
        embedding_model=os.getenv(
            "EMBEDDING_MODEL",
            RetrievalConfig.embedding_model,
        ),
        top_k=int(os.getenv("TOP_K", RetrievalConfig.top_k)),
        relevance_threshold=float(
            os.getenv("RELEVANCE_THRESHOLD", RetrievalConfig.relevance_threshold)
        ),
        min_supporting_chunks=int(
            os.getenv(
                "MIN_SUPPORTING_CHUNKS",
                RetrievalConfig.min_supporting_chunks,
            )
        ),
    )
    decision = DecisionConfig(
        answer_threshold=float(
            os.getenv("ANSWER_THRESHOLD", DecisionConfig.answer_threshold)
        ),
        clarification_threshold=float(
            os.getenv(
                "CLARIFICATION_THRESHOLD",
                DecisionConfig.clarification_threshold,
            )
        ),
        unsupported_answer_threshold=float(
            os.getenv(
                "UNSUPPORTED_ANSWER_THRESHOLD",
                DecisionConfig.unsupported_answer_threshold,
            )
        ),
    )
    confidence = ConfidenceConfig(
        ambiguity_score_threshold=float(
            os.getenv(
                "AMBIGUITY_SCORE_THRESHOLD",
                ConfidenceConfig.ambiguity_score_threshold,
            )
        ),
        no_evidence_threshold=float(
            os.getenv(
                "NO_EVIDENCE_THRESHOLD",
                ConfidenceConfig.no_evidence_threshold,
            )
        ),
    )
    return AppConfig(
        paths=paths,
        chunking=ChunkingConfig(),
        retrieval=retrieval,
        llm=llm,
        confidence=confidence,
        decision=decision,
    )


def ensure_runtime_dirs(config: AppConfig | None = None) -> None:
    cfg = config or get_config()
    for directory in (
        cfg.paths.indices_dir,
        cfg.paths.logs_dir,
        cfg.paths.sample_docs_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
