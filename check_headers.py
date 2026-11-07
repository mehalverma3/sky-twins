import os
import requests

key = os.environ["ANTHROPIC_API_KEY"]
model = os.environ["LLM_MODEL"]
url = "https://opencode.ai/zen/v1/chat/completions"
body = {"model": model, "max_tokens": 30,
        "messages": [{"role": "user", "content": "Say hi"}]}

for label, headers in [
    ("bearer only", {"Authorization": f"Bearer {key}"}),
    ("x-api-key only", {"x-api-key": key}),
    ("both", {"Authorization": f"Bearer {key}", "x-api-key": key}),
]:
    r = requests.post(url, json=body, headers=headers, timeout=30)
    print(label, "->", r.status_code, r.text[:200])