from __future__ import annotations

import re

from core.config import AppConfig
from core.schemas import GeneratedAnswer, RetrievedChunk
from generation.llm import MultiProviderLLM
from generation.prompts import GROUNDING_SYSTEM_PROMPT, build_answer_prompt


class GroundedAnswerer:
    def __init__(self, config: AppConfig, llm: MultiProviderLLM) -> None:
        self.config = config
        self.llm = llm

    def answer(
        self,
        query: str,
        evidence: list[RetrievedChunk],
        *,
        provider_name: str | None = None,
        llm_model: str | None = None,
        llm_api_key: str | None = None,
        llm_base_url: str | None = None,
    ) -> GeneratedAnswer:
        if not evidence:
            return GeneratedAnswer(
                text="The retrieved evidence is insufficient to support a reliable answer.",
                grounded=True,
                insufficient_evidence=True,
            )

        context = self._build_context(evidence)
        llm_response = self.llm.generate(
            system_prompt=GROUNDING_SYSTEM_PROMPT,
            user_prompt=build_answer_prompt(query, context),
            provider_name=provider_name,
            model_name=llm_model,
            api_key=llm_api_key,
            base_url=llm_base_url,
        )
        citations = [
            hit.chunk_id
            for hit in evidence
            if hit.score >= self.config.retrieval.relevance_threshold
        ][:3]

        if llm_response and llm_response.text:
            lowered = llm_response.text.lower()
            return GeneratedAnswer(
                text=llm_response.text,
                citations=citations,
                generator_mode=llm_response.mode,
                grounded=True,
                insufficient_evidence=(
                    "insufficient" in lowered or "not enough" in lowered
                ),
            )

        return self._fallback_answer(query, evidence, citations)

    @staticmethod
    def _build_context(evidence: list[RetrievedChunk]) -> str:
        blocks = []
        for hit in evidence:
            source = f"{hit.file_name}"
            if hit.page_number:
                source += f", page {hit.page_number}"
            blocks.append(f"[{hit.chunk_id}] ({source}, score={hit.score:.2f})\n{hit.text}")
        return "\n\n".join(blocks)

    def _fallback_answer(
        self,
        query: str,
        evidence: list[RetrievedChunk],
        citations: list[str],
    ) -> GeneratedAnswer:
        strong_hits = [
            hit for hit in evidence if hit.score >= self.config.retrieval.relevance_threshold
        ]
        if not strong_hits:
            return GeneratedAnswer(
                text="The retrieved evidence is insufficient to support a reliable answer.",
                citations=[],
                generator_mode="fallback",
                grounded=True,
                insufficient_evidence=True,
            )

        query_terms = _tokenize(query)
        candidate_sentences: list[tuple[int, str]] = []
        for hit in strong_hits[:2]:
            for sentence in re.split(r"(?<=[.!?])\s+", hit.text):
                cleaned = sentence.strip()
                if not cleaned:
                    continue
                overlap = len(query_terms & _tokenize(cleaned))
                candidate_sentences.append((overlap, cleaned))
        candidate_sentences.sort(key=lambda item: item[0], reverse=True)
        if candidate_sentences and candidate_sentences[0][0] < 2:
            return GeneratedAnswer(
                text="The retrieved evidence is insufficient to support a reliable answer.",
                citations=[],
                generator_mode="fallback",
                grounded=True,
                insufficient_evidence=True,
            )
        summary = self._compose_fallback_summary(candidate_sentences, strong_hits)
        if not summary:
            summary = self._clean_sentence(strong_hits[0].text.strip())
        answer_text = summary
        return GeneratedAnswer(
            text=answer_text,
            citations=citations or [strong_hits[0].chunk_id],
            generator_mode="fallback",
            grounded=True,
            insufficient_evidence=False,
        )

    def _compose_fallback_summary(
        self,
        candidate_sentences: list[tuple[int, str]],
        strong_hits: list[RetrievedChunk],
    ) -> str:
        selected: list[str] = []
        for overlap, sentence in candidate_sentences:
            if overlap <= 0:
                continue
            cleaned = self._clean_sentence(sentence)
            if not cleaned or cleaned in selected:
                continue
            selected.append(cleaned)
            if len(" ".join(selected)) >= 320 or len(selected) >= 2:
                break
        if not selected and strong_hits:
            first_sentence = re.split(r"(?<=[.!?])\s+", strong_hits[0].text.strip())[0]
            cleaned = self._clean_sentence(first_sentence)
            if cleaned:
                selected.append(cleaned)
        summary = " ".join(selected).strip()
        return re.sub(r"\s+", " ", summary)[:360].strip()

    @staticmethod
    def _clean_sentence(sentence: str) -> str:
        cleaned = re.sub(
            r"^(chapter\s+\d+\s+|preface\s+to\s+the\s+first\s+edition\s+|[\divxlcdm]+\s+\d+\s+introduction\s+)",
            "",
            sentence.strip(),
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip(" -:")


def _tokenize(text: str) -> set[str]:
    stopwords = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "from",
        "have",
        "what",
        "about",
        "does",
        "your",
        "which",
        "into",
        "when",
        "were",
        "their",
        "after",
        "before",
        "should",
        "could",
        "would",
        "there",
        "was",
        "who",
        "why",
        "how",
        "say",
        "says",
        "it",
    }
    return {
        token
        for token in re.findall(r"[A-Za-z0-9]+", text.lower())
        if len(token) > 2 and token not in stopwords
    }
