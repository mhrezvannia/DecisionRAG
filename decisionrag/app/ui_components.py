from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from core.schemas import DecisionType, IndexBuildResult, QueryResult, RetrievedChunk


def render_header() -> None:
    st.markdown(
        """
        <div class="dr-hero">
            <div class="dr-kicker">Research Engineering Portfolio Project</div>
            <div class="dr-hero-grid">
                <div>
                    <div class="dr-title">DecisionRAG</div>
                    <div class="dr-subtitle">Uncertainty-Aware Retrieval-Augmented Decision System</div>
                    <div class="dr-body">
                        A document-grounded QA system that retrieves evidence, estimates confidence, and decides whether to answer,
                        request clarification, or abstain.
                    </div>
                </div>
                <div class="dr-hero-panel">
                    <div class="dr-mini-label">System Flow</div>
                    <div class="dr-flow-stack">
                        <span class="dr-chip">Retriever</span>
                        <span class="dr-flow-arrow">-&gt;</span>
                        <span class="dr-chip">Grounded Generator</span>
                        <span class="dr-flow-arrow">-&gt;</span>
                        <span class="dr-chip">Confidence Estimator</span>
                        <span class="dr-flow-arrow">-&gt;</span>
                        <span class="dr-chip">Decision Policy</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(kicker: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="dr-section-intro">
            <div class="dr-kicker">{escape(kicker)}</div>
            <div class="dr-section-title">{escape(title)}</div>
            <div class="dr-body">{escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_tiles(
    *,
    provider_label: str,
    provider_ready: bool,
    model_name: str,
    corpus_summary: str,
    pipeline_summary: str,
) -> None:
    provider_state = "Live API" if provider_ready else "Fallback"
    provider_hint = (
        "Generation is running with the configured provider."
        if provider_ready
        else "Retrieval, confidence, and policy remain active even without a live model."
    )
    tiles = [
        ("Provider", provider_label, f"{provider_state} | {model_name}", provider_hint),
        (
            "Corpus",
            corpus_summary,
            "Indexed state",
            "Use the sample corpus or upload your own files and rebuild the index when needed.",
        ),
        (
            "Policy",
            "Answer | Clarify | Abstain",
            "Decision modes",
            pipeline_summary,
        ),
    ]

    columns = st.columns(3, gap="large")
    for column, (label, value, subvalue, body) in zip(columns, tiles):
        column.markdown(
            f"""
            <div class="dr-status-tile">
                <div class="dr-mini-label">{escape(label)}</div>
                <div class="dr-status-value">{escape(value)}</div>
                <div class="dr-status-subvalue">{escape(subvalue)}</div>
                <div class="dr-status-body">{escape(body)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_build_summary(summary: IndexBuildResult) -> None:
    st.success(
        f"Index ready: {summary.chunk_count} chunks from {summary.document_count} documents."
    )
    if summary.file_names:
        st.caption("Indexed files: " + ", ".join(summary.file_names))
    if summary.ingestion_errors:
        st.warning("Some files could not be parsed:")
        for error in summary.ingestion_errors:
            st.write(f"- {error}")


def render_decision_badge(decision: DecisionType) -> None:
    css_class = {
        DecisionType.ANSWER: "decision-answer",
        DecisionType.ASK_FOR_CLARIFICATION: "decision-clarify",
        DecisionType.ABSTAIN: "decision-abstain",
    }[decision]
    label = decision.value.replace("_", " ")
    st.markdown(
        f'<span class="decision-badge {css_class}">{label}</span>',
        unsafe_allow_html=True,
    )


def render_result_summary(result: QueryResult) -> None:
    render_decision_badge(result.decision.decision)
    st.markdown(
        f'<div class="dr-result-copy">{escape(result.decision.response_text)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="dr-result-note">{escape(result.decision.rationale)}</div>',
        unsafe_allow_html=True,
    )
    if result.decision.override_reasons:
        for note in result.decision.override_reasons:
            st.markdown(
                f'<div class="dr-inline-note">{escape(note)}</div>',
                unsafe_allow_html=True,
            )


def evidence_dataframe(evidence: list[RetrievedChunk]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Rank": hit.rank,
                "Source": hit.file_name,
                "Page": hit.page_number if hit.page_number else "-",
                "Similarity": round(hit.score, 3),
            }
            for hit in evidence
        ]
    )


def render_evidence(evidence: list[RetrievedChunk]) -> None:
    if not evidence:
        st.info("No evidence retrieved yet.")
        return
    st.dataframe(evidence_dataframe(evidence), use_container_width=True, hide_index=True)
    for hit in evidence:
        page_text = f"page {hit.page_number}" if hit.page_number else "text chunk"
        with st.expander(
            f"Evidence {hit.rank} | {hit.file_name} | {page_text} | similarity {hit.score:.2f}",
            expanded=(hit.rank == 1),
        ):
            st.markdown(
                f"""
                <div class="dr-evidence-card">
                    <div class="dr-evidence-head">
                        <span class="source-chip">Rank {hit.rank}</span>
                        <span class="source-chip">{escape(hit.file_name)}</span>
                        <span class="source-chip">{escape(page_text)}</span>
                        <span class="source-chip">similarity {hit.score:.2f}</span>
                    </div>
                    <div class="dr-evidence-text">{escape(hit.text)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_debug(result: QueryResult) -> None:
    st.json(
        {
            "ambiguity": result.ambiguity.model_dump(),
            "confidence": result.confidence.model_dump(),
            "decision": result.decision.model_dump(),
            "answer": result.answer.model_dump(),
            "retrieval": [hit.model_dump() for hit in result.evidence],
        }
    )
