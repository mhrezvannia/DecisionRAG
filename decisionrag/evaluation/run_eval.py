from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from core.schemas import EvalExample
from core.utils import DecisionRAGPipeline
from evaluation.metrics import compute_decision_metrics


def main() -> None:
    pipeline = DecisionRAGPipeline()
    sample_docs = pipeline.list_sample_docs()
    build_summary = pipeline.build_index(local_paths=sample_docs, index_name="evaluation_index")
    dataset_path = PROJECT_ROOT / "evaluation" / "eval_dataset.json"
    dataset = [
        EvalExample.model_validate(item)
        for item in json.loads(dataset_path.read_text(encoding="utf-8"))
    ]

    records: list[dict] = []
    for example in dataset:
        result = pipeline.run_query(example.query, index_name="evaluation_index")
        records.append(
            {
                "query": example.query,
                "expected_decision": example.expected_decision.value,
                "predicted_decision": result.decision.decision.value,
                "confidence": result.confidence.total_confidence,
                "notes": example.notes,
            }
        )

    metrics = compute_decision_metrics(records)
    output_path = PROJECT_ROOT / "evaluation" / "eval_results.json"
    output_path.write_text(
        json.dumps(
            {
                "build_summary": build_summary.model_dump(),
                "metrics": metrics,
                "records": records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("DecisionRAG evaluation complete")
    print(f"Examples: {metrics['num_examples']}")
    print(f"Decision accuracy: {metrics['decision_accuracy']:.2%}")
    print(f"Abstention rate: {metrics['abstention_rate']:.2%}")
    print(f"Clarification rate: {metrics['clarification_rate']:.2%}")
    print(f"Counts per decision: {metrics['counts_per_decision']}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
