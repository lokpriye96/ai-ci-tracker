"""LLM adapters. Plain REST calls, so no vendor SDK is required.

Provider is chosen with the CI_LLM_PROVIDER environment variable:
  gemini    (default; free tier available)  needs GEMINI_API_KEY
  anthropic                                  needs ANTHROPIC_API_KEY
  openai                                     needs OPENAI_API_KEY
  mock      (offline; returns a fixture, used by tests and demos)
Model names change often, so each can be overridden with CI_LLM_MODEL.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import requests

DEFAULT_MODELS = {
    "gemini": "auto",  # picks the newest Flash-Lite / Flash model the key can use
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-4.1-mini",
}

# JSON schema the model must follow (kept simple so every provider accepts it)
EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "event_date": {"type": "string"},
                    "date_precision": {"type": "string"},
                    "event_type": {"type": "string"},
                    "counterparty": {"type": "string"},
                    "counterparty_type": {"type": "string"},
                    "headline": {"type": "string"},
                    "summary": {"type": "string"},
                    "strategic_theme": {"type": "string"},
                    "industry_focus": {"type": "string"},
                    "deal_value_usd_m": {"type": "number", "nullable": True},
                    "value_note": {"type": "string"},
                    "evidence_quote": {"type": "string"},
                    "confidence": {"type": "string"},
                },
                "required": ["company", "event_date", "event_type", "headline",
                             "summary", "strategic_theme", "evidence_quote", "confidence"],
            },
        }
    },
    "required": ["events"],
}


def _parse_json(text: str) -> dict:
    """Accept raw JSON or JSON wrapped in ``` fences."""
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0) if m else text)


_GEMINI_MODEL_CACHE: dict = {}


def pick_gemini_model(key: str) -> str:
    """Choose a fast, non-thinking Gemini model available to this key (cached)."""
    if "name" in _GEMINI_MODEL_CACHE:
        return _GEMINI_MODEL_CACHE["name"]
    r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}&pageSize=200",
                     timeout=30)
    r.raise_for_status()
    names = [m["name"].split("/")[-1] for m in r.json().get("models", [])
             if "generateContent" in m.get("supportedGenerationMethods", [])]
    stable = [n for n in names if "preview" not in n and "exp" not in n
              and "tts" not in n and "image" not in n and "audio" not in n]
    for pref in ("flash-lite", "flash"):
        cands = sorted((n for n in stable if pref in n), reverse=True)
        if cands:
            # prefer explicit versions (e.g. gemini-2.5-flash-lite) over "-latest" aliases
            versioned = [n for n in cands if any(ch.isdigit() for ch in n)]
            _GEMINI_MODEL_CACHE["name"] = (versioned or cands)[0]
            print(f"    Gemini model selected: {_GEMINI_MODEL_CACHE['name']}", flush=True)
            return _GEMINI_MODEL_CACHE["name"]
    raise RuntimeError(f"No Flash model available to this key; saw {names[:10]}")


def call_llm(prompt: str) -> dict:
    provider = os.getenv("CI_LLM_PROVIDER", "gemini").lower()
    model = os.getenv("CI_LLM_MODEL", DEFAULT_MODELS.get(provider, ""))

    if provider == "mock":
        fixture = Path(os.getenv("CI_MOCK_RESPONSE", "tests/fixtures/mock_llm_response.json"))
        return json.loads(fixture.read_text(encoding="utf-8"))

    if provider == "gemini":
        import time
        key = os.environ["GEMINI_API_KEY"]
        if model in ("", "auto"):
            model = pick_gemini_model(key)
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
               f"?key={key}")
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json",
                                 "maxOutputTokens": 2048},
        }
        r = None
        for attempt in range(4):
            try:
                r = requests.post(url, json=body, timeout=60)
            except requests.Timeout:
                if attempt < 3:
                    continue
                raise RuntimeError(f"Gemini ({model}) timed out 4 times")
            if r.status_code in (429, 500, 503) and attempt < 3:  # free-tier limits: back off
                time.sleep(15 * (attempt + 1))
                continue
            break
        if r.status_code != 200:
            raise RuntimeError(f"Gemini ({model}) HTTP {r.status_code}: {r.text[:300]}")
        parts = r.json()["candidates"][0]["content"]["parts"]
        return _parse_json("".join(p.get("text", "") for p in parts))

    if provider == "anthropic":
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                     "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": model, "max_tokens": 2000, "temperature": 0,
                  "messages": [{"role": "user", "content": prompt + "\n\nReturn only JSON."}]},
            timeout=90,
        )
        r.raise_for_status()
        return _parse_json(r.json()["content"][0]["text"])

    if provider == "openai":
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
            json={"model": model, "temperature": 0,
                  "response_format": {"type": "json_object"},
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=90,
        )
        r.raise_for_status()
        return _parse_json(r.json()["choices"][0]["message"]["content"])

    raise ValueError(f"Unknown CI_LLM_PROVIDER: {provider}")
