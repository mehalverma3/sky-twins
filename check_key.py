import os
import anthropic

key = os.environ.get("ANTHROPIC_API_KEY")
print("Key present:", bool(key), "| length:", len(key) if key else 0,
      "| starts with:", key[:7] if key else None)

try:
    msg = anthropic.Anthropic(api_key=key).messages.create(
        model="claude-sonnet-5-5",
        max_tokens=20,
        messages=[{"role": "user", "content": "Say hi"}],
    )
    print("SUCCESS:", msg.content[0].text)
except Exception as e:
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR MESSAGE:", e)