from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from core.config import AppConfig
from core.schemas import DocumentChunk, IndexBuildResult


class FaissIndexer:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def build_and_save(
        self,
        *,
        chunks: list[DocumentChunk],
        embeddings: np.ndarray,
        index_name: str,
    ) -> IndexBuildResult:
        if embeddings.size == 0:
            raise ValueError("Embeddings are empty. Index build cannot continue.")
        output_dir = self.config.paths.indices_dir / index_name
        output_dir.mkdir(parents=True, exist_ok=True)
        index_path = output_dir / "index.faiss"
        metadata_path = output_dir / "metadata.json"

        normalized = embeddings.copy()
        faiss.normalize_L2(normalized)
        index = faiss.IndexFlatIP(normalized.shape[1])
        index.add(normalized)
        faiss.write_index(index, str(index_path))

        metadata = {
            "embedding_model": self.config.retrieval.embedding_model,
            "dimension": normalized.shape[1],
            "chunks": [chunk.model_dump() for chunk in chunks],
        }
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return IndexBuildResult(
            index_name=index_name,
            index_path=str(index_path),
            metadata_path=str(metadata_path),
            document_count=len({chunk.file_name for chunk in chunks}),
            chunk_count=len(chunks),
            file_names=sorted({chunk.file_name for chunk in chunks}),
        )

    def load(self, index_name: str) -> tuple[faiss.IndexFlatIP, list[DocumentChunk], dict]:
        index_dir = self.config.paths.indices_dir / index_name
        index_path = index_dir / "index.faiss"
        metadata_path = index_dir / "metadata.json"
        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"Index '{index_name}' was not found. Build the index before querying."
            )
        index = faiss.read_index(str(index_path))
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        chunks = [DocumentChunk.model_validate(item) for item in metadata["chunks"]]
        return index, chunks, metadata
