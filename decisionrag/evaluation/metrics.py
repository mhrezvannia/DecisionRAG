from __future__ import annotations

from collections import Counter, defaultdict


def compute_decision_metrics(records: list[dict]) -> dict:
    total = len(records)
    correct = sum(
        1 for record in records if record["expected_decision"] == record["predicted_decision"]
    )
    predicted_counts = Counter(record["predicted_decision"] for record in records)
    confidence_by_decision: dict[str, list[float]] = defaultdict(list)
    for record in records:
        confidence_by_decision[record["predicted_decision"]].append(record["confidence"])
    average_confidence = {
        decision: sum(values) / len(values)
        for decision, values in confidence_by_decision.items()
    }
    return {
        "decision_accuracy": correct / total if total else 0.0,
        "abstention_rate": predicted_counts.get("ABSTAIN", 0) / total if total else 0.0,
        "clarification_rate": (
            predicted_counts.get("ASK_FOR_CLARIFICATION", 0) / total if total else 0.0
        ),
        "counts_per_decision": dict(predicted_counts),
        "average_confidence_by_decision": average_confidence,
        "num_examples": total,
    }
