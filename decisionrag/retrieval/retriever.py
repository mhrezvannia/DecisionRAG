from __future__ import annotations

from typing import Sequence

import faiss
import numpy as np

from core.config import AppConfig
from core.schemas import RetrievedChunk
from retrieval.embedder import SentenceTransformerEmbedder
from retrieval.indexer import FaissIndexer


class Retriever:
    def __init__(
        self,
        config: AppConfig,
        embedder: SentenceTransformerEmbedder,
        indexer: FaissIndexer,
    ) -> None:
        self.config = config
        self.embedder = embedder
        self.indexer = indexer

    def retrieve(
        self,
        query: str,
        *,
        index_name: str = "default",
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        index, chunks, _ = self.indexer.load(index_name)
        if not chunks:
            return []
        query_vector = self.embedder.encode_query(query).reshape(1, -1).astype("float32")
        faiss.normalize_L2(query_vector)
        limit = min(top_k or self.config.retrieval.top_k, len(chunks))
        scores, indices = index.search(query_vector, limit)
        results: list[RetrievedChunk] = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
            if idx < 0:
                continue
            chunk = chunks[int(idx)]
            normalized_score = float(np.clip((float(score) + 1.0) / 2.0, 0.0, 1.0))
            results.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    file_name=chunk.file_name,
                    page_number=chunk.page_number,
                    text=chunk.text,
                    score=normalized_score,
                    rank=rank,
                )
            )
        return results
