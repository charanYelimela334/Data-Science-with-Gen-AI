# File: backend/apps/parser/rag/vector_store.py
# Purpose: ChromaDB client for storing and retrieving resume examples.
# App: parser

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import chromadb

from .embedder import get_embedding


# Determine the path for ChromaDB storage
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CHROMA_DATA_DIR = os.path.join(BASE_DIR, "apps", "parser", "chroma_data")


class ResumeVectorStore:
    def __init__(self):
        # Ensure the directory exists
        os.makedirs(CHROMA_DATA_DIR, exist_ok=True)
        # Initialize the ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=CHROMA_DATA_DIR)
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name="resume_examples",
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )

    def add_resume(self, user_id: str, raw_text: str, json_output: Dict[str, Any], verified: bool) -> None:
        """
        Upsert a resume into the vector store.
        - id: string representation of user_id (enables upsert)
        - raw_text: truncated to 3000 chars
        - json_output: serialized to JSON string in metadata
        - verified: boolean flag in metadata
        """
        if not raw_text:
            return
            
        doc_id = str(user_id)
        truncated_text = raw_text[:3000]
        embedding = get_embedding(truncated_text)
        
        metadata = {
            "json_output": json.dumps(json_output),
            "verified": verified
        }

        # Upsert adds or updates based on the ID
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[truncated_text],
            metadatas=[metadata]
        )

    def query_similar(self, resume_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar verified resumes.
        Returns a list of dictionaries with 'resume_text', 'json_output', 'verified', and 'similarity'.
        """
        if not resume_text:
            return []

        embedding = get_embedding(resume_text[:8000])

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where={"verified": True},
            include=["documents", "metadatas", "distances"]
        )

        similar_resumes = []
        if not results or not results["ids"] or not results["ids"][0]:
            return similar_resumes

        # Extract the inner lists (since we only queried for 1 embedding)
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(documents)):
            # Cosine distance to similarity: similarity = 1 - distance
            # (Assuming ChromaDB returns cosine distance for 'cosine' space)
            distance = distances[i]
            similarity = 1.0 - distance

            metadata = metadatas[i]
            json_output = json.loads(metadata["json_output"])
            verified = metadata["verified"]

            similar_resumes.append({
                "resume_text": documents[i],
                "json_output": json_output,
                "verified": verified,
                "similarity": similarity
            })

        return similar_resumes

# Expose a singleton instance for easier importing
vector_store = ResumeVectorStore()
