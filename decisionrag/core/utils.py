from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from core.config import AppConfig, ensure_runtime_dirs, get_config
from core.logging_utils import append_jsonl, build_log_entry
from core.schemas import IndexBuildResult, QueryResult
from decision.ambiguity import AmbiguityDetector
from decision.policy import DecisionPolicy
from generation.answerer import GroundedAnswerer
from generation.llm import MultiProviderLLM
from ingestion.chunker import Chunker
from ingestion.loader import load_documents_from_paths, load_documents_from_uploads
from retrieval.embedder import SentenceTransformerEmbedder
from retrieval.indexer import FaissIndexer
from retrieval.retriever import Retriever
from uncertainty.confidence import ConfidenceEstimator


class DecisionRAGPipeline:
    """Shared orchestration layer used by the app and evaluation scripts."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or get_config()
        ensure_runtime_dirs(self.config)
        self.embedder = SentenceTransformerEmbedder(self.config.retrieval.embedding_model)
        self.indexer = FaissIndexer(self.config)
        self.retriever = Retriever(self.config, self.embedder, self.indexer)
        self.llm = MultiProviderLLM(self.config.llm)
        self.answerer = GroundedAnswerer(self.config, self.llm)
        self.ambiguity_detector = AmbiguityDetector(self.config)
        self.confidence_estimator = ConfidenceEstimator(self.config)
        self.decision_policy = DecisionPolicy(self.config)
        self.chunker = Chunker(self.config.chunking)

    def build_index(
        self,
        *,
        local_paths: Sequence[Path] | None = None,
        uploaded_files: Sequence[Any] | None = None,
        index_name: str = "default",
    ) -> IndexBuildResult:
        documents = []
        errors: list[str] = []
        if local_paths:
            loaded_docs, path_errors = load_documents_from_paths(local_paths)
            documents.extend(loaded_docs)
            errors.extend(path_errors)
        if uploaded_files:
            upload_docs, upload_errors = load_documents_from_uploads(uploaded_files)
            documents.extend(upload_docs)
            errors.extend(upload_errors)
        if not documents:
            raise ValueError("No documents were loaded. Add sample files or upload documents first.")

        chunks = self.chunker.chunk_documents(documents)
        if not chunks:
            raise ValueError("Document parsing succeeded, but chunking produced no usable text.")

        embeddings = self.embedder.encode_texts([chunk.text for chunk in chunks])
        build_result = self.indexer.build_and_save(
            chunks=chunks,
            embeddings=embeddings,
            index_name=index_name,
        )
        build_result.ingestion_errors = errors
        return build_result

    def run_query(
        self,
        query: str,
        *,
        index_name: str = "default",
        top_k: int | None = None,
        answer_threshold: float | None = None,
        clarification_threshold: float | None = None,
        provider_name: str | None = None,
        llm_model: str | None = None,
        llm_api_key: str | None = None,
        llm_base_url: str | None = None,
    ) -> QueryResult:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        evidence = self.retriever.retrieve(query, index_name=index_name, top_k=top_k)
        ambiguity = self.ambiguity_detector.assess(query)
        answer = self.answerer.answer(
            query,
            evidence,
            provider_name=provider_name,
            llm_model=llm_model,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
        )
        confidence = self.confidence_estimator.estimate(query, evidence, answer, ambiguity)
        decision = self.decision_policy.decide(
            confidence=confidence,
            ambiguity=ambiguity,
            answer=answer,
            evidence=evidence,
            answer_threshold=answer_threshold,
            clarification_threshold=clarification_threshold,
        )
        result = QueryResult(
            query=query,
            ambiguity=ambiguity,
            answer=answer,
            confidence=confidence,
            decision=decision,
            evidence=evidence,
        )
        append_jsonl(self.config.paths.logs_dir / "interactions.jsonl", build_log_entry(result))
        return result

    def list_sample_docs(self) -> list[Path]:
        return sorted(
            path
            for path in self.config.paths.sample_docs_dir.iterdir()
            if path.suffix.lower() in {".pdf", ".txt", ".md"}
        )

    def load_index_metadata(self, index_name: str = "default") -> dict[str, Any] | None:
        metadata_path = self.config.paths.indices_dir / index_name / "metadata.json"
        if not metadata_path.exists():
            return None
        return json.loads(metadata_path.read_text(encoding="utf-8"))
