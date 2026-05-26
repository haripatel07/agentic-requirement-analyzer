"""Agent 2 — Requirement Analysis

analyze_requirements(state: dict) -> dict
"""
import os
import json
import time
import re
from typing import Dict

PROMPT = """
You are a requirements extraction assistant. Read the provided document
and return ONLY valid JSON with three keys: "actors", "features",
and "constraints". Each value must be a list of short strings.

Example output format:
{
  "actors": ["User", "Administrator"],
  "features": ["User registration with email confirmation", "Product search"],
  "constraints": ["Support up to 10,000 catalog items", "PCI-compliant payments"]
}

One-shot example (anchor):
Input text: "The system must allow users to reset passwords via an OTP sent
to their phone. Admins should be able to revoke sessions."

Expected JSON: {"actors": ["User", "Admin"], "features": ["Password reset via OTP", "Session revocation by admin"], "constraints": []}

Now analyze the following document and produce only the JSON described above.
Document:
"""


def _call_groq(prompt_text: str) -> str:
    # Try to use langchain-groq ChatGroq if available
    try:
        from langchain_groq import ChatGroq
        client = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))
        # The exact method may vary by library version; attempt a common pattern
        resp = client.chat([{"role": "user", "content": prompt_text}], model="llama-3.3-70b-versatile")
        # resp may be a string or an object; coerce to string
        if isinstance(resp, str):
            return resp
        # try common attributes
        if hasattr(resp, "content"):
            return resp.content
        if isinstance(resp, (list, tuple)) and len(resp) > 0:
            first = resp[0]
            return getattr(first, "content", str(first))
        return str(resp)
    except Exception as e:
        raise


def _extract_json(text: str) -> Dict:
    try:
        return json.loads(text)
    except Exception:
        # Try to extract first JSON object with braces
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    raise ValueError("Could not parse JSON from model response")


def analyze_requirements(state: Dict) -> Dict:
    raw = state.get("raw_text", "")
    prompt = PROMPT + "\n" + raw
    errors = []
    attempts = 2
    last_exc = None
    for attempt in range(attempts):
        try:
            resp_text = _call_groq(prompt)
            parsed = _extract_json(resp_text)
            # Ensure keys exist and are lists
            actors = parsed.get("actors", []) or []
            features = parsed.get("features", []) or []
            constraints = parsed.get("constraints", []) or []
            # Coerce to lists of strings
            actors = [str(a).strip() for a in actors]
            features = [str(f).strip() for f in features]
            constraints = [str(c).strip() for c in constraints]
            return {"actors": actors, "features": features, "constraints": constraints}
        except Exception as e:
            last_exc = e
            errors.append(str(e))
            time.sleep(1)
            continue
    return {"actors": [], "features": [], "constraints": [], "errors": errors}


if __name__ == "__main__":
    # quick local test: read sample docs and run analyzer
    sample = os.path.join(os.path.dirname(__file__), "..", "..", "sample_docs", "sample_requirement.txt")
    sample = os.path.abspath(sample)
    try:
        with open(sample, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        raw = ""
    state = {"raw_text": raw}
    out = analyze_requirements(state)
    print(out)
