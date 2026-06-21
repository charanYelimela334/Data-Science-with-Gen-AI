# File: backend/apps/parser/pdf_extractor.py
# Purpose: Extract text content from uploaded PDF resumes.
# App: parser

from __future__ import annotations

import io

import pypdfium2 as pdfium


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text_parts: list[str] = []
    pdf = pdfium.PdfDocument(pdf_bytes)
    for i in range(len(pdf)):
        page = pdf[i]
        textpage = page.get_textpage()
        text_parts.append(textpage.get_text_bounded() or "")
    return "\n".join(text_parts).strip()

