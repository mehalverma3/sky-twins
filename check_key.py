import os
import anthropic

key = os.environ.get("ANTHROPIC_API_KEY")
base = os.environ.get("ANTHROPIC_BASE_URL")
model = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")
print("Key present:", bool(key), "| base URL:", base, "| model:", model)

try:
    msg = anthropic.Anthropic(api_key=key, base_url=base).messages.create(
        model=model, max_tokens=20,
        messages=[{"role": "user", "content": "Say hi"}],
    )
    print("SUCCESS:", msg.content[0].text)
except Exception as e:
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR MESSAGE:", e)