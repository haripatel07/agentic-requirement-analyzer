"""Agent 4 — User Story Generation

generate_user_stories(state: dict) -> dict
"""
import os
import json
import time
import re
from typing import Dict, List

PROMPT = """
You are a user-story generator. For each functional requirement provided,
generate one Agile user story in the form: "As a <actor>, I want <action>
so that <benefit>" and assign a priority (High/Medium/Low) inferred from
context. Return ONLY valid JSON: {"user_stories": [{"feature": ..., "story": ..., "priority": ...}, ...]}

Example:
{"user_stories": [{"feature": "User registration", "story": "As a Visitor, I want to register with email so that I can place orders", "priority": "High"}]}

Now generate stories for the following functional requirements.
"""


def _call_groq(prompt_text: str) -> str:
    try:
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it to .env and restart backend.")
        client = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=api_key,
        )
        resp = client.invoke(prompt_text)
        if hasattr(resp, "content"):
            return resp.content
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


def _dedupe_user_stories(stories: List[Dict]) -> List[Dict]:
    seen = set()
    out = []
    for story in stories:
        feature = str(story.get("feature", "")).strip()
        text = str(story.get("story", "")).strip()
        priority = str(story.get("priority", "Medium")).strip() or "Medium"
        if not text:
            continue
        key = (feature.lower(), text.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append({"feature": feature, "story": text, "priority": priority})
    return out


def generate_user_stories(state: Dict) -> Dict:
    frs: List[str] = state.get("functional_requirements", []) or []
    raw = state.get("raw_text", "")
    prompt = PROMPT + json.dumps({"functional_requirements": frs}, indent=2) + "\nDocument:\n" + raw
    errors = []
    attempts = 2
    for attempt in range(attempts):
        try:
            resp_text = _call_groq(prompt)
            parsed = _extract_json(resp_text)
            stories = parsed.get("user_stories", []) or []
            # normalize
            normalized = []
            for s in stories:
                normalized.append({
                    "feature": str(s.get("feature") if isinstance(s, dict) else s).strip(),
                    "story": str(s.get("story") if isinstance(s, dict) else s).strip(),
                    "priority": str(s.get("priority", "Medium") if isinstance(s, dict) else "Medium").strip(),
                })
            return {"user_stories": _dedupe_user_stories(normalized)}
        except Exception as e:
            errors.append(str(e))
            time.sleep(1)
            continue
    return {"user_stories": [], "errors": errors}


if __name__ == "__main__":
    sample = os.path.join(os.path.dirname(__file__), "..", "..", "sample_docs", "sample_requirement.txt")
    try:
        with open(sample, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        raw = ""
    state = {"functional_requirements": ["User can register with email"], "raw_text": raw}
    print(generate_user_stories(state))
