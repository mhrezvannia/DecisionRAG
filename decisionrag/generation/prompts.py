GROUNDING_SYSTEM_PROMPT = """You are a careful document-grounded assistant.
Use only the retrieved evidence.
Do not add facts that are not explicitly supported by the evidence.
If the evidence is insufficient or ambiguous, say so plainly."""


def build_answer_prompt(query: str, evidence_block: str) -> str:
    return f"""Answer the question using only the retrieved evidence below.

Question:
{query}

Retrieved evidence:
{evidence_block}

Requirements:
- Ground the answer in the evidence only.
- Keep the answer concise and factual.
- If the evidence is insufficient, respond by saying the evidence is insufficient.
- Do not speculate or invent details.
"""
