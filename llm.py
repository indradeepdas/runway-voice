"""Optional LLM narration layer.

Every number in an answer is computed by the deterministic cash engine
(cash_model.py + brain.py). When RUNWAY_LLM_API_KEY is set, this layer only
re-phrases the computed facts into natural spoken language - it never sees
raw model inputs and is instructed never to invent a figure, so a bad
completion cannot produce a wrong number (the caller falls back to the
deterministic template on any failure or empty result).

Zero-cost by default: with no key configured, nothing here runs.
"""
import json
import os
import urllib.request


def narrate(question, facts_text, history=None, model_state=None):
    """Return a natural-language phrasing of facts_text, or None to fall back."""
    key = os.environ.get("RUNWAY_LLM_API_KEY")
    if not key:
        return None
    base_url = os.environ.get("RUNWAY_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("RUNWAY_LLM_MODEL", "gpt-4o-mini")
    system = (
        "You are the voice of Runway Voice, a cash copilot for SMB founders. "
        "Rewrite the computed answer below into one short spoken-style paragraph. "
        "Hard rules: use ONLY the euro figures and week numbers that appear in the "
        "computed answer - never invent, estimate, or round any number; add no advice "
        "beyond what is stated; maximum 60 words. "
        f"Context: {model_state or 'fictional demo company, 13-week cash window'}."
    )
    messages = [{"role": "system", "content": system}]
    for q, a in (history or [])[-6:]:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a["text"] if isinstance(a, dict) else str(a)})
    messages.append({"role": "user", "content": f"Question: {question}\nComputed answer: {facts_text}"})
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 220,
    }).encode()
    req = urllib.request.Request(
        f"{base_url}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        text = (data["choices"][0]["message"]["content"] or "").strip()
        return text or None
    except Exception:
        return None  # unreachable/invalid endpoint: deterministic answer stands
