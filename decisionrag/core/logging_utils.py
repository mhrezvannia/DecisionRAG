from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from core.schemas import LogEntry, QueryResult


def build_log_entry(result: QueryResult) -> LogEntry:
    return LogEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        query=result.query,
        decision=result.decision.decision.value,
        confidence=result.confidence.total_confidence,
        component_scores=result.confidence.components.model_dump(),
        retrieved_sources=[
            {
                "chunk_id": hit.chunk_id,
                "file_name": hit.file_name,
                "page_number": hit.page_number,
                "score": hit.score,
            }
            for hit in result.evidence
        ],
        generated_response=result.decision.response_text,
        rationale=result.decision.rationale,
    )


def append_jsonl(log_path: Path, entry: LogEntry) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.model_dump(), ensure_ascii=False) + "\n")
