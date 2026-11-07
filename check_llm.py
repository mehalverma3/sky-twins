import os
import requests

key = os.environ["ANTHROPIC_API_KEY"]  # reusing the variable you already set
model = os.environ.get("LLM_MODEL", "")
base = "https://opencode.ai/zen/v1"
print("model:", "console-trava-security/gpt-6-luna")

for path, body in [
    ("/chat/completions", {"model": "console-trava-security/gpt-6-luna", "max_tokens": 30,
                           "messages": [{"role": "user", "content": "Say hi"}]}),
    ("/responses", {"model": "console-trava-security/gpt-6-luna", "input": "Say hi"}),
]:
    r = requests.post(base + path, json=body, timeout=30,
                      headers={"Authorization": f"Bearer {key}"})
    print(path, "->", r.status_code, r.text[:300])