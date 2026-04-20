from __future__ import annotations

import re
from dataclasses import dataclass

from core.schemas import DocumentChunk, LoadedDocument


@dataclass
class Chunker:
    config: object

    def chunk_documents(self, documents: list[LoadedDocument]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for document in documents:
            chunks.extend(self._chunk_single_document(document))
        return chunks

    def _chunk_single_document(self, document: LoadedDocument) -> list[DocumentChunk]:
        paragraphs = self._split_paragraphs(document.text)
        target = self.config.target_chunk_chars
        overlap = self.config.overlap_chars
        minimum = self.config.min_chunk_chars
        current: list[str] = []
        current_length = 0
        chunks: list[DocumentChunk] = []

        for paragraph in paragraphs:
            paragraph_length = len(paragraph)
            if current and current_length + paragraph_length > target and current_length >= minimum:
                chunks.append(
                    self._make_chunk(document, len(chunks), current)
                )
                current = self._overlap_tail(current, overlap)
                current_length = sum(len(part) for part in current)
            current.append(paragraph)
            current_length += paragraph_length

        if current:
            if chunks and current_length < minimum:
                previous = chunks.pop()
                merged_text = previous.text + "\n\n" + "\n\n".join(current)
                chunks.append(
                    DocumentChunk(
                        chunk_id=previous.chunk_id,
                        file_name=document.file_name,
                        text=merged_text.strip(),
                        page_number=document.page_number,
                        chunk_index=previous.chunk_index,
                    )
                )
            else:
                chunks.append(self._make_chunk(document, len(chunks), current))
        return chunks

    @staticmethod
    def _split_paragraphs(text: str) -> list[str]:
        normalized = text.replace("\r\n", "\n")
        paragraphs = [
            re.sub(r"\s+", " ", part).strip()
            for part in re.split(r"\n\s*\n", normalized)
            if part.strip()
        ]
        if paragraphs:
            return paragraphs
        return [re.sub(r"\s+", " ", normalized).strip()]

    @staticmethod
    def _overlap_tail(paragraphs: list[str], overlap_chars: int) -> list[str]:
        tail: list[str] = []
        length = 0
        for paragraph in reversed(paragraphs):
            tail.insert(0, paragraph)
            length += len(paragraph)
            if length >= overlap_chars:
                break
        return tail

    @staticmethod
    def _make_chunk(document: LoadedDocument, chunk_index: int, parts: list[str]) -> DocumentChunk:
        page_token = f"p{document.page_number}" if document.page_number else "p0"
        chunk_id = f"{document.file_name}-{page_token}-c{chunk_index}"
        return DocumentChunk(
            chunk_id=chunk_id,
            file_name=document.file_name,
            text="\n\n".join(parts).strip(),
            page_number=document.page_number,
            chunk_index=chunk_index,
        )
