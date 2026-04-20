from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import fitz

from core.schemas import LoadedDocument


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_documents_from_paths(paths: Sequence[Path]) -> tuple[list[LoadedDocument], list[str]]:
    documents: list[LoadedDocument] = []
    errors: list[str] = []
    for path in paths:
        try:
            documents.extend(_load_single_path(Path(path)))
        except Exception as exc:  # pragma: no cover - defensive path
            errors.append(f"{Path(path).name}: {exc}")
    return documents, errors


def load_documents_from_uploads(uploaded_files: Sequence[Any]) -> tuple[list[LoadedDocument], list[str]]:
    documents: list[LoadedDocument] = []
    errors: list[str] = []
    for uploaded in uploaded_files:
        try:
            file_name = getattr(uploaded, "name", "uploaded_document")
            content = uploaded.getvalue() if hasattr(uploaded, "getvalue") else uploaded.read()
            documents.extend(_load_bytes(file_name, content))
        except Exception as exc:  # pragma: no cover - defensive path
            errors.append(f"{getattr(uploaded, 'name', 'uploaded_document')}: {exc}")
    return documents, errors


def _load_single_path(path: Path) -> list[LoadedDocument]:
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")
    return _load_bytes(path.name, path.read_bytes())


def _load_bytes(file_name: str, content: bytes) -> list[LoadedDocument]:
    extension = Path(file_name).suffix.lower()
    if extension == ".pdf":
        return _load_pdf(file_name, content)
    if extension in {".txt", ".md"}:
        text = content.decode("utf-8", errors="ignore").strip()
        if not text:
            return []
        return [LoadedDocument(file_name=file_name, text=text)]
    raise ValueError(f"Unsupported file type: {extension}")


def _load_pdf(file_name: str, content: bytes) -> list[LoadedDocument]:
    documents: list[LoadedDocument] = []
    pdf = fitz.open(stream=content, filetype="pdf")
    try:
        for page_index, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if text:
                documents.append(
                    LoadedDocument(
                        file_name=file_name,
                        text=text,
                        page_number=page_index,
                    )
                )
    finally:
        pdf.close()
    return documents
