"""Utilities for extracting raw text from resume documents."""
from __future__ import annotations

import io
from typing import Callable

from fastapi import UploadFile

try:  # pragma: no cover - optional dependency
    from docling.document import Document  # type: ignore
    from docling.pipeline import Pipeline
    _HAS_DOCLING = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_DOCLING = False
    Pipeline = Document = None  # type: ignore

from pypdf import PdfReader
from docx import Document as DocxDocument

TEXT_CHUNK_LIMIT = 15000


def _read_with_docling(file_bytes: bytes, file_name: str) -> str:
    if not _HAS_DOCLING:
        raise RuntimeError("Docling is not installed")

    pipeline = Pipeline()
    document: Document = pipeline.run(io.BytesIO(file_bytes), file_name=file_name)
    text_segments: list[str] = []
    for page in document.pages:
        text_segments.append(page.text)
    return "\n".join(text_segments)


def _read_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_segments: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_segments.append(page_text)
    return "\n".join(text_segments)


def _read_docx(file_bytes: bytes) -> str:
    document = DocxDocument(io.BytesIO(file_bytes))
    text_segments: list[str] = []
    for paragraph in document.paragraphs:
        text_segments.append(paragraph.text)
    return "\n".join(text_segments)


def _fallback(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(upload: UploadFile) -> str:
    file_bytes = upload.file.read()
    file_name = upload.filename or "resume"

    readers: list[tuple[str, Callable[[bytes], str]]] = []
    if _HAS_DOCLING:
        readers.append(("docling", lambda data: _read_with_docling(data, file_name)))

    if file_name.lower().endswith(".pdf"):
        readers.extend([("pdf", _read_pdf), ("fallback", _fallback)])
    elif file_name.lower().endswith(".docx"):
        readers.extend([("docx", _read_docx), ("fallback", _fallback)])
    else:
        readers.extend([("pdf", _read_pdf), ("docx", _read_docx), ("fallback", _fallback)])

    last_error: Exception | None = None
    for _, reader in readers:
        try:
            text = reader(file_bytes)
            text = "\n".join(line.strip() for line in text.splitlines())
            if len(text) > TEXT_CHUNK_LIMIT:
                text = text[:TEXT_CHUNK_LIMIT]
            return text
        except Exception as exc:  # pragma: no cover - best effort extraction
            last_error = exc
            continue

    raise RuntimeError("Failed to extract text from resume") from last_error
