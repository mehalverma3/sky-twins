import os
import re

import requests

BASE_URL = os.environ.get("LLM_BASE_URL", "https://opencode.ai/zen/v1")
MODEL = os.environ.get("LLM_MODEL", "")

def write_reading(target_date: str, twins: list[dict]) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or not MODEL:
        return "Reading unavailable: no API key or model configured."
    prompt, valid_ids = build_prompt(target_date, twins)
    try:
        r = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": MODEL,
                "max_tokens": 600,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=45,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Reading unavailable right now ({type(e).__name__})."
    if not is_grounded(text, valid_ids):
        return "The generated reading cited events that weren't retrieved, so it was discarded."
    return text