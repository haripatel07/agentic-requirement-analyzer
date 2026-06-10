"""Agent 5 — Acceptance Criteria Generation

generate_acceptance_criteria(state: dict) -> dict
"""
import os
import json
import time
import re
from typing import Dict, List

PROMPT = """
You are an acceptance-criteria generator. For each user story provided,
generate Given/When/Then acceptance criteria. Return ONLY valid JSON:
{"acceptance_criteria": [{"story_ref": <story or index>, "given": ..., "when": ..., "then": ...}, ...]}

Example:
{"acceptance_criteria": [{"story_ref": "As a Visitor...", "given": "Given a visitor", "when": "When they submit registration form", "then": "Then they receive a confirmation email"}]}

Now generate criteria for the following user stories.
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


def generate_acceptance_criteria(state: Dict) -> Dict:
    stories: List[Dict] = state.get("user_stories", []) or []
    raw = state.get("raw_text", "")
    prompt = PROMPT + json.dumps({"user_stories": stories}, indent=2) + "\nDocument:\n" + raw
    errors = []
    attempts = 2
    for attempt in range(attempts):
        try:
            resp_text = _call_groq(prompt)
            parsed = _extract_json(resp_text)
            criteria = parsed.get("acceptance_criteria", []) or []
            normalized = []
            for c in criteria:
                normalized.append({
                    "story_ref": c.get("story_ref") if isinstance(c, dict) else c,
                    "given": c.get("given") if isinstance(c, dict) else "",
                    "when": c.get("when") if isinstance(c, dict) else "",
                    "then": c.get("then") if isinstance(c, dict) else "",
                })
            return {"acceptance_criteria": normalized}
        except Exception as e:
            errors.append(str(e))
            time.sleep(1)
            continue
    return {"acceptance_criteria": [], "errors": errors}


if __name__ == "__main__":
    state = {"user_stories": [{"story": "As a Visitor, I want to register with email so that I can place orders"}]}
    print(generate_acceptance_criteria(state))
