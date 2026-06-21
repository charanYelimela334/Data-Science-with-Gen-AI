# File: backend/apps/parser/rag/vector_store.py
# Purpose: Lightweight JSON-based vector store for storing and retrieving resume examples.
# App: parser

from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, List

from .embedder import get_embedding


# Determine the path for JSON storage
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "apps", "parser", "rag_data")
DB_FILE = os.path.join(DATA_DIR, "vector_db.json")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


class ResumeVectorStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        
    def _load_data(self) -> List[Dict[str, Any]]:
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_resume(self, user_id: str, raw_text: str, json_output: Dict[str, Any], verified: bool) -> None:
        """
        Upsert a resume into the lightweight JSON vector store.
        """
        if not raw_text:
            return
            
        doc_id = str(user_id)
        truncated_text = raw_text[:3000]
        embedding = get_embedding(truncated_text)
        
        data = self._load_data()
        
        new_entry = {
            "id": doc_id,
            "embedding": embedding,
            "raw_text": truncated_text,
            "json_output": json.dumps(json_output),
            "verified": verified
        }

        # Check if exists to upsert
        updated = False
        for i, entry in enumerate(data):
            if entry.get("id") == doc_id:
                data[i] = new_entry
                updated = True
                break
        
        if not updated:
            data.append(new_entry)
            
        self._save_data(data)

    def query_similar(self, resume_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Query the lightweight vector store for similar verified resumes.
        """
        if not resume_text:
            return []

        query_embedding = get_embedding(resume_text[:8000])
        data = self._load_data()
        
        results = []
        for entry in data:
            if not entry.get("verified"):
                continue
                
            sim = cosine_similarity(query_embedding, entry["embedding"])
            results.append({
                "resume_text": entry["raw_text"],
                "json_output": json.loads(entry["json_output"]),
                "verified": entry["verified"],
                "similarity": sim
            })

        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]


# Expose a singleton instance
vector_store = ResumeVectorStore()
