# File: backend/apps/parser/gpt_extractor.py
# Purpose: Convert raw resume text into structured JSON via GPT-4o.
# App: parser

from __future__ import annotations

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class ResumeParsingError(RuntimeError):
    """Raised when LLM resume parsing fails in a recoverable way."""


def parse_resume_with_gpt(prompt: str) -> Dict[str, Any]:
    try:
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise ResumeParsingError(
                "OPENAI_API_KEY is missing in backend/.env."
            )

        base_url = (os.getenv("OPENAI_BASE_URL") or "").strip() or None
        model = (os.getenv("OPENAI_MODEL") or "gpt-4o").strip()

        default_headers = {}
        if base_url and "openrouter.ai" in base_url:
            # OpenRouter recommends these headers for ranking/analytics.
            referer = (os.getenv("OPENROUTER_SITE_URL") or "").strip()
            app_name = (os.getenv("OPENROUTER_APP_NAME") or "").strip()
            if referer:
                default_headers["HTTP-Referer"] = referer
            if app_name:
                default_headers["X-Title"] = app_name

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=default_headers or None,
        )
        completion = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        content = (completion.choices[0].message.content or "{}").strip()
        # Fallback stripping just in case
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except ResumeParsingError:
        raise
    except json.JSONDecodeError as exc:
        raise ResumeParsingError(
            "Model returned invalid JSON. Please retry with a clearer resume PDF."
        ) from exc
    except Exception as exc:
        message = str(exc)
        if "invalid_api_key" in message or "Incorrect API key provided" in message:
            raise ResumeParsingError(
                "Invalid API key. Update OPENAI_API_KEY in backend/.env."
            ) from exc
        raise ResumeParsingError(f"Failed to parse resume with GPT: {message}") from exc

