from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.styles import APP_CSS
from app.ui_components import (
    render_build_summary,
    render_debug,
    render_evidence,
    render_header,
    render_result_summary,
    render_section_intro,
    render_status_tiles,
)
from core.config import get_config
from core.utils import DecisionRAGPipeline


PROVIDER_OPTIONS = {
    "openai": "OpenAI",
    "gemini": "Gemini",
    "llama": "Llama-Compatible",
}


@st.cache_resource
def get_pipeline() -> DecisionRAGPipeline:
    return DecisionRAGPipeline(get_config())


def _build_corpus_summary(index_summary: object | None) -> str:
    if hasattr(index_summary, "document_count") and hasattr(index_summary, "chunk_count"):
        return f"{index_summary.document_count} docs / {index_summary.chunk_count} chunks"
    if isinstance(index_summary, dict):
        chunk_count = len(index_summary.get("chunks", []))
        file_names = {chunk.get("file_name") for chunk in index_summary.get("chunks", [])}
        return f"{len(file_names)} docs / {chunk_count} chunks"
    return "No active index"


def main() -> None:
    st.set_page_config(
        page_title="DecisionRAG",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(APP_CSS, unsafe_allow_html=True)

    config = get_config()
    pipeline = get_pipeline()
    metadata = pipeline.load_index_metadata("demo_index")

    if "index_summary" not in st.session_state and metadata:
        st.session_state["index_summary"] = metadata
    if "query_result" not in st.session_state:
        st.session_state["query_result"] = None
    if "query_text" not in st.session_state:
        st.session_state["query_text"] = ""

    provider_name = (
        config.llm.default_provider
        if config.llm.default_provider in PROVIDER_OPTIONS
        else "gemini"
    )
    provider_defaults = getattr(config.llm, provider_name)
    runtime = pipeline.llm.resolve_runtime(
        provider_name=provider_name,
        model_name=provider_defaults.model_name,
        api_key=provider_defaults.api_key,
        base_url=provider_defaults.base_url,
    )
    provider_ready = pipeline.llm.is_available(runtime)
    index_summary = st.session_state.get("index_summary")
    current_index_summary = index_summary

    if current_index_summary is None:
        current_index_summary = st.session_state.get("index_summary")

    with st.sidebar:
        st.markdown("## Retrieval Controls")
        top_k = st.slider("Top-k retrieval", min_value=2, max_value=6, value=config.retrieval.top_k)
        answer_threshold = st.slider(
            "Answer threshold",
            min_value=0.60,
            max_value=0.90,
            value=float(config.decision.answer_threshold),
            step=0.01,
        )
        clarification_threshold = st.slider(
            "Clarification threshold",
            min_value=0.25,
            max_value=0.70,
            value=float(config.decision.clarification_threshold),
            step=0.01,
        )
        debug = st.toggle("Debug panel", value=True)
        st.caption("Adjust retrieval depth and decision thresholds for the current corpus.")

    sample_docs = pipeline.list_sample_docs()
    render_header()
    render_status_tiles(
        provider_label=PROVIDER_OPTIONS[provider_name],
        provider_ready=provider_ready,
        model_name=runtime.model_name,
        corpus_summary=_build_corpus_summary(current_index_summary),
        pipeline_summary="Confidence combines retrieval relevance, evidence coverage, answer support, ambiguity, and insufficiency.",
    )

    setup_col, query_col = st.columns([0.95, 1.35], gap="large")

    with setup_col:
        with st.container(border=True):
            render_section_intro(
                "Corpus Setup",
                "Load Documents and Build the Index",
                "Use the bundled sample documents or upload your own files, then rebuild the FAISS index for retrieval.",
            )
            use_sample_docs = st.checkbox("Use bundled sample documents", value=True)
            if sample_docs:
                st.caption("Bundled docs: " + ", ".join(path.name for path in sample_docs))
            uploaded_files = st.file_uploader(
                "Upload PDF, TXT, or Markdown files",
                type=["pdf", "txt", "md"],
                accept_multiple_files=True,
            )
            if st.button("Build Corpus Index", use_container_width=True):
                try:
                    local_paths = sample_docs if use_sample_docs else []
                    with st.spinner("Parsing documents, chunking text, embedding chunks, and building the FAISS index..."):
                        build_summary = pipeline.build_index(
                            local_paths=local_paths,
                            uploaded_files=uploaded_files or [],
                            index_name="demo_index",
                        )
                    st.session_state["index_summary"] = build_summary
                    index_summary = build_summary
                    current_index_summary = build_summary
                except Exception as exc:
                    st.error(str(exc))

            if index_summary and not isinstance(index_summary, dict):
                render_build_summary(index_summary)

    with query_col:
        with st.container(border=True):
            render_section_intro(
                "Decision Workspace",
                "Ask a Grounded Question",
                "Run retrieval, grounded generation, confidence scoring, and uncertainty-aware decision logic over the indexed corpus.",
            )
            example_cols = st.columns(3, gap="small")
            example_queries = [
                "What deployment requirement is needed before the system can recommend an answer?",
                "Explain this result.",
                "What GPU cluster was used for training?",
            ]
            for column, example in zip(example_cols, example_queries):
                if column.button(example, use_container_width=True):
                    st.session_state["query_text"] = example
                    st.rerun()

            query = st.text_area(
                "Query",
                key="query_text",
                height=140,
                placeholder="Ask a question about the indexed document set...",
            )

            action_col, info_col = st.columns([0.22, 0.78], gap="medium")
            start_clicked = action_col.button(
                "Start",
                type="primary",
                use_container_width=True,
                disabled=not bool(query.strip()),
            )
            info_col.caption(
                "The system will answer only when evidence and confidence are strong enough; otherwise it will clarify or abstain."
            )

            if start_clicked:
                try:
                    with st.spinner("Running retrieval, grounded generation, confidence scoring, and decision policy..."):
                        result = pipeline.run_query(
                            query,
                            index_name="demo_index",
                            top_k=top_k,
                            answer_threshold=answer_threshold,
                            clarification_threshold=clarification_threshold,
                            provider_name=provider_name,
                            llm_model=runtime.model_name,
                            llm_api_key=runtime.api_key,
                            llm_base_url=runtime.base_url,
                        )
                    st.session_state["query_result"] = result
                except Exception as exc:
                    st.error(str(exc))

    result = st.session_state.get("query_result")
    if result:
        st.divider()
        result_col, diagnostics_col = st.columns([1.35, 0.9], gap="large")

        with result_col:
            with st.container(border=True):
                render_section_intro(
                    "Decision Output",
                    "Final System Response",
                    "This is the final policy-mediated output after retrieval, grounding, confidence scoring, and uncertainty-aware decision logic.",
                )
                render_result_summary(result)

        with diagnostics_col:
            with st.container(border=True):
                render_section_intro(
                    "Diagnostics",
                    "Confidence Snapshot",
                    "A compact summary of the current query outcome and model behavior.",
                )
                left_metric, right_metric = st.columns(2)
                left_metric.metric("Confidence", f"{result.confidence.total_confidence:.2f}")
                right_metric.metric("Generator", result.answer.generator_mode.upper())
                st.metric("Evidence Chunks", len(result.evidence))
                st.caption(
                    "Confidence signals: retrieval relevance, evidence coverage, answer support, ambiguity penalty, insufficiency penalty."
                )

        st.divider()
        with st.container(border=True):
            render_section_intro(
                "Retrieved Evidence",
                "Top Supporting Chunks",
                "These passages are the only evidence the generator is supposed to use.",
            )
            render_evidence(result.evidence)

        if debug:
            with st.expander("Debug Panel", expanded=False):
                render_debug(result)


if __name__ == "__main__":
    main()
