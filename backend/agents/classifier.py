"""Agent 3 — Requirement Classification

classify_requirements(state: dict) -> dict
"""
import os
import json
import time
import re
from typing import Dict

PROMPT = """
You are a requirements classifier. Given the document and a list of
features/constraints, return ONLY valid JSON with two keys:
"functional_requirements" and "non_functional_requirements". Each must
be a list of short strings.

Guidance: Features like Login, Registration, Payment are functional.
Security, Scalability, Performance, Availability are typically
non-functional.

Example output:
{"functional_requirements": ["User can register with email"], "non_functional_requirements": ["System must be PCI-compliant"]}

Now classify the following features and constraints from the document.
Features/Constraints:
"""


def _call_groq(prompt_text: str) -> str:
    try:
        from langchain_groq import ChatGroq
        client = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))
        resp = client.chat([{"role": "user", "content": prompt_text}], model="llama-3.3-70b-versatile")
        if isinstance(resp, str):
            return resp
        if hasattr(resp, "content"):
            return resp.content
        if isinstance(resp, (list, tuple)) and len(resp) > 0:
            first = resp[0]
            return getattr(first, "content", str(first))
        return str(resp)
    except Exception:
        raise


def _extract_json(text: str) -> Dict:
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    raise ValueError("Could not parse JSON from model response")


def classify_requirements(state: Dict) -> Dict:
    features = state.get("features", []) or []
    constraints = state.get("constraints", []) or []
    raw = state.get("raw_text", "")
    payload = PROMPT + json.dumps({"features": features, "constraints": constraints}, indent=2) + "\nDocument:\n" + raw
    errors = []
    attempts = 2
    for attempt in range(attempts):
        try:
            resp_text = _call_groq(payload)
            parsed = _extract_json(resp_text)
            fr = parsed.get("functional_requirements", []) or []
            nfr = parsed.get("non_functional_requirements", []) or []
            fr = [str(x).strip() for x in fr]
            nfr = [str(x).strip() for x in nfr]
            return {"functional_requirements": fr, "non_functional_requirements": nfr}
        except Exception as e:
            errors.append(str(e))
            time.sleep(1)
            continue
    return {"functional_requirements": [], "non_functional_requirements": [], "errors": errors}


if __name__ == "__main__":
    sample = os.path.join(os.path.dirname(__file__), "..", "..", "sample_docs", "sample_requirement.txt")
    sample = os.path.abspath(sample)
    try:
        with open(sample, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        raw = ""
    # naive test: set features/constraints to some heuristics
    state = {"features": ["User registration with email", "Product search"], "constraints": ["Support up to 10,000 items"], "raw_text": raw}
    out = classify_requirements(state)
    print(out)
