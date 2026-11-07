"""Grounded readings: the model may only cite events we retrieved."""
import os
import re

import requests

try:
    import streamlit as st
except ImportError:  # lets tests and scripts run without Streamlit
    st = None

DEFAULT_BASE_URL = "https://opencode.ai/zen/v1"

SYSTEM = """You write short, thoughtful readings for an astrology-curious audience.
Rules:
- Use ONLY the historical events provided. Never add outside history.
- Cite every event you reference with its tag, like [E1].
- Present the reading as interpretation, not scientific prediction.
- Be honest: if the matched events are mostly dramatic, say this reflects what history records, not a verdict on the day.
- Keep it under 200 words."""


def get_setting(name: str, default: str = "") -> str:
    """Environment variable first, then Streamlit secrets, else default."""
    val = os.environ.get(name)
    if not val and st is not None:
        try:
            if name in st.secrets:
                val = str(st.secrets[name])
        except Exception:  # no secrets file, or running outside Streamlit
            val = None
    if not val:
        return default
    return val.strip().strip('"').strip("'").strip()


def build_prompt(target_date: str, twins: list[dict]):
    """Return (prompt, valid_ids). Each event gets a tag like E1, E2, ..."""
    lines, valid_ids, n = [], set(), 0
    for twin in twins:
        lines.append(f"Sky twin: {twin['date']} (similarity {twin['score']})")
        for ev in twin["events"]:
            n += 1
            valid_ids.add(f"E{n}")
            lines.append(f"  [E{n}] {twin['date']}: {ev['text']}")
    prompt = (
        f"Target date: {target_date}\n\n"
        + "\n".join(lines)
        + "\n\nWrite the reading for the target date."
    )
    return prompt, valid_ids


def cited_ids(text: str) -> set:
    """All event tags cited in brackets, e.g. [E1], [E1, E2], [E1][E2]."""
    ids = set()
    for group in re.findall(r"\[([^\]]*)\]", text):
        ids.update(re.findall(r"E\d+", group))
    return ids


def is_grounded(text: str, valid_ids: set) -> bool:
    ids = cited_ids(text)
    return bool(ids) and ids <= valid_ids


def _extract_text(data: dict) -> str:
    """Pull reply text out of a chat/completions response."""
    content = data["choices"][0]["message"].get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):  # some providers return a list of parts
        parts = [p.get("text", "") for p in content if isinstance(p, dict)]
        return "".join(parts).strip()
    return ""


def write_reading(target_date: str, twins: list[dict]) -> str:
    key = get_setting("LLM_API_KEY") or get_setting("ANTHROPIC_API_KEY")
    model = get_setting("LLM_MODEL")
    base_url = get_setting("LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")

    if not key:
        return "Reading unavailable: no API key configured."
    if not model:
        return "Reading unavailable: no model configured (set LLM_MODEL)."

    prompt, valid_ids = build_prompt(target_date, twins)
    if not valid_ids:
        return "Reading unavailable: no events were retrieved to base it on."

    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "max_tokens": 1200,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=60,
        )
    except requests.RequestException as e:
        return f"Reading unavailable: could not reach the model service ({type(e).__name__})."

    if resp.status_code != 200:
        return f"Reading unavailable: model service returned {resp.status_code}: {resp.text[:200]}"

    try:
        text = _extract_text(resp.json())
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        return "Reading unavailable: unexpected response format from the model service."

    if not text:
        return "Reading unavailable: the model returned an empty reply."
    if not is_grounded(text, valid_ids):
        return "The generated reading cited events that weren't retrieved, so it was discarded."
    return text


if __name__ == "__main__":
    # Quick self-test: python reading.py (needs your exports set)
    sample = [{
        "date": "1969-07-20",
        "score": 0.95,
        "events": [{"text": "Apollo 11 lands on the Moon", "page_title": "", "url": ""}],
    }]
    print(write_reading("2000-01-01", sample))