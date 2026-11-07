"""Grounded readings: the model may only cite events we retrieved."""
import os
import re
from datetime import date

import requests

try:
    import streamlit as st
except ImportError:
    st = None

DEFAULT_BASE_URL = "https://opencode.ai/zen/v1"
MAX_TOKENS = 1500

SYSTEM = """You write short, thoughtful readings for an astrology-curious audience.
Rules:
- Use ONLY the historical events provided. Never add outside history.
- Cite every event you reference with its tag, like [E1].
- Present the reading as interpretation, not scientific prediction.
- Be honest: if the matched events are mostly dramatic, say this reflects what history records, not a verdict on the day.
- Keep it under 200 words."""


def get_setting(name: str, default: str = "") -> str:
    val = os.environ.get(name)
    if not val and st is not None:
        try:
            if name in st.secrets:
                val = str(st.secrets[name])
        except Exception:
            val = None
    if not val:
        return default
    return val.strip().strip('"').strip("'").strip()


def build_prompt(target_date: str, twins: list):
    lines, valid_ids, n = [], set(), 0
    for twin in twins:
        lines.append(f"Sky twin: {twin['date']} (similarity {twin['score']})")
        for ev in twin["events"]:
            n += 1
            valid_ids.add(f"E{n}")
            lines.append(f"  [E{n}] {twin['date']}: {ev['text']}")
    note = ""
    try:
        if date.fromisoformat(target_date) > date.today():
            note = ("\nNote: the target date is in the future. Frame the reading as "
                    "what these past sky twins suggest, not as a forecast.")
    except ValueError:
        pass
    prompt = (
        f"Target date: {target_date}\n\n"
        + "\n".join(lines)
        + note
        + "\n\nWrite the reading for the target date."
    )
    return prompt, valid_ids


def cited_ids(text: str) -> set:
    ids = set()
    for group in re.findall(r"\[([^\]]*)\]", text):
        ids.update(re.findall(r"E\d+", group))
    return ids


def is_grounded(text: str, valid_ids: set) -> bool:
    ids = cited_ids(text)
    return bool(ids) and ids <= valid_ids


def _extract_text(data: dict) -> str:
    if isinstance(data.get("output_text"), str):
        return data["output_text"].strip()
    if data.get("choices"):
        content = data["choices"][0].get("message", {}).get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            return "".join(
                p.get("text", "") for p in content if isinstance(p, dict)
            ).strip()
    parts = []
    for item in data.get("output") or []:
        for c in item.get("content") or []:
            if isinstance(c, dict) and isinstance(c.get("text"), str):
                parts.append(c["text"])
    return "".join(parts).strip()


def _headers(key: str) -> dict:
    return {
        "Authorization": f"Bearer {key}",
        "x-api-key": key,
        "Content-Type": "application/json",
    }


def _chat_payload(model: str, prompt: str, token_param: str) -> dict:
    return {
        "model": model,
        token_param: MAX_TOKENS,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    }


def _responses_payload(model: str, prompt: str) -> dict:
    return {
        "model": model,
        "instructions": SYSTEM,
        "input": prompt,
        "max_output_tokens": MAX_TOKENS,
    }


def _call_model(base_url: str, key: str, model: str, prompt: str):
    headers = _headers(key)
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=_chat_payload(model, prompt, "max_tokens"),
        timeout=60,
    )
    if resp.status_code == 400 and "max_completion_tokens" in resp.text:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=_chat_payload(model, prompt, "max_completion_tokens"),
            timeout=60,
        )
    if resp.status_code in (404, 405):
        resp = requests.post(
            f"{base_url}/responses",
            headers=headers,
            json=_responses_payload(model, prompt),
            timeout=60,
        )
    return resp


def write_reading(target_date: str, twins: list) -> str:
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
        resp = _call_model(base_url, key, model, prompt)
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
    sample = [{
        "date": "1969-07-20",
        "score": 0.95,
        "events": [{"text": "Apollo 11 lands on the Moon", "page_title": "", "url": ""}],
    }]
    print(write_reading("2000-01-01", sample))
