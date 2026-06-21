# File: backend/apps/parser/rag/few_shot_builder.py
# Purpose: Build the final prompt for GPT-4o, incorporating few-shot examples if available.
# App: parser

from __future__ import annotations

import json
from typing import Any, Dict, List

def _get_schema_instructions() -> str:
    return (
        "You are a strict JSON resume parser. Return only valid JSON.\n"
        "Use exactly this schema keys: basic_info, skills, experience, projects, education, certifications.\n"
        "basic_info must include: first_name, last_name, email, phone, dob, location, linkedin, github.\n"
        "skills is an array of objects: {skill_name, level} where level is Beginner|Intermediate|Expert.\n"
        "experience objects: {title, company, duration, description, responsibilities}.\n"
        "projects objects: {title, description, technologies, duration}.\n"
        "education objects: {degree, institution, year, cgpa}.\n"
        "certifications objects: {name, issuer, year}.\n"
        "Use null for missing values, never empty strings.\n"
        "No markdown, no explanations, no extra keys."
    )

def build_extraction_prompt(new_resume_text: str, examples: List[Dict[str, Any]]) -> str:
    """
    Constructs the prompt for GPT-4o structured extraction.
    If examples are provided, truncates each to 1500 chars and includes them as few-shot examples.
    """
    prompt = _get_schema_instructions() + "\n\n"

    if examples:
        prompt += "Below are some examples of successfully parsed resumes:\n\n"
        for i, ex in enumerate(examples[:3]):
            # Truncate example text to 1500 chars to avoid prompt bloat
            ex_text = ex.get("resume_text", "")[:1500]
            ex_json = ex.get("json_output", {})
            prompt += f"--- Example {i+1} ---\n"
            prompt += f"RAW RESUME (truncated):\n{ex_text}\n\n"
            prompt += f"EXTRACTED JSON:\n{json.dumps(ex_json, indent=2)}\n\n"
        prompt += "--- End of Examples ---\n\n"

    prompt += "Now, parse the following new resume:\n\n"
    prompt += f"RAW RESUME:\n{new_resume_text}\n"

    return prompt
