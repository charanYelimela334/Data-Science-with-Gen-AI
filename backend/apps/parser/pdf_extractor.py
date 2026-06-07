# File: backend/apps/parser/pdf_extractor.py
# Purpose: Extract text content from uploaded PDF resumes.
# App: parser

from __future__ import annotations

import io

import pdfplumber


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()

