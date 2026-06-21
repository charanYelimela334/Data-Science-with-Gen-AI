# File: backend/apps/parser/rag/embedder.py
# Purpose: Generate embeddings for resume text using OpenAI.
# App: parser

from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def get_embedding(text: str) -> List[float]:
    """
    Get the embedding vector for a given text using OpenAI's text-embedding-3-small.
    Truncates the input text to 8000 characters to fit within limits.
    """
    if not text:
        return []

    # Truncate text to 8000 chars
    text = text[:8000]

    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing in backend/.env.")

    client = OpenAI(api_key=api_key)
    
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    
    return response.data[0].embedding
