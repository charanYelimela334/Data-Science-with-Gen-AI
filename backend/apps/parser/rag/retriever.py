# File: backend/apps/parser/rag/retriever.py
# Purpose: Retrieve few-shot examples from the vector store for RAG.
# App: parser

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .vector_store import vector_store

logger = logging.getLogger(__name__)

MIN_SIMILARITY_THRESHOLD = 0.5

def get_few_shot_examples(new_resume_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve up to top_k similar verified resumes from the vector store.
    Filters out results that do not meet MIN_SIMILARITY_THRESHOLD.
    NEVER raises an exception; returns an empty list on failure.
    """
    try:
        if not new_resume_text:
            return []

        results = vector_store.query_similar(new_resume_text, top_k=top_k)
        
        filtered_results = [
            res for res in results 
            if res.get("similarity", 0) >= MIN_SIMILARITY_THRESHOLD
        ]
        
        return filtered_results
    except Exception as e:
        # RAG should never block core parsing; fail gracefully.
        logger.warning(f"Failed to retrieve few-shot examples: {e}")
        return []
