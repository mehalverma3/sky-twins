import os
import re

import anthropic

MODEL = "console-trava-security/gpt-6-luna"  # confirm the current model string in the Anthropic console docs

SYSTEM = """You write short, thoughtful readings for an astrology-curious audience.
Rules:
- Use ONLY the historical events provided. Never add outside history.
- Cite every event you reference with its tag, like [E1].
- Present the reading as interpretation, not scientific prediction.
- Be honest: if the matched events are mostly dramatic, say this reflects what history records, not a verdict on the day.
- Keep it under 200 words."""


def build_prompt(target_date: str, twins: list[dict]):
    lines, valid_ids, n = [], set(), 0
    for twin in twins:
        lines.append(f"Sky twin: {twin['date']} (similarity {twin['score']})")
        for ev in twin["events"]:
            n += 1
            valid_ids.add(f"E{n}")
            lines.append(f"  [E{n}] {twin['date']}: {ev['text']}")
    prompt = (f"Target date: {target_date}\n\n" + "\n".join(lines) +
              "\n\nWrite the reading for the target date.")
    return prompt, valid_ids


def cited_ids(text: str) -> set:
    return set(re.findall(r"\[(E\d+)\]", text))


def is_grounded(text: str, valid_ids: set) -> bool:
    ids = cited_ids(text)
    return bool(ids) and ids <= valid_ids


def write_reading(target_date: str, twins: list[dict]) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return "Reading unavailable: no API key configured."
    prompt, valid_ids = build_prompt(target_date, twins)
    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model=MODEL, max_tokens=600, system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text
    except Exception as e:
        return f"Reading unavailable right now ({type(e).__name__})."
    if not is_grounded(text, valid_ids):
        return "The generated reading cited events that weren't retrieved, so it was discarded."
    return text