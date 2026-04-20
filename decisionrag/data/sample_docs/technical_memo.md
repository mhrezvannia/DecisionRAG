# Technical Memo: Retrieval and Decision Policy

The retrieval index is built from PDF, Markdown, and text documents. Chunks are approximately 500 to 700 characters with overlap so that important details are not split across unrelated boundaries.

The system should recommend an answer only when confidence is at least 0.80 and the retrieved evidence includes at least two passages above 0.60 similarity. This requirement is intended to prevent premature answers.

Questions with vague references such as "what does it say?" or "explain this" should trigger an ambiguity flag and a clarification request.

If no API key is configured, the application should still perform retrieval and confidence scoring while using a retrieval-grounded fallback response instead of an external LLM.
