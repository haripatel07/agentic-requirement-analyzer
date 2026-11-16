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
Do NOT start the given/when/then values with the words "Given", "When" or "Then"; the UI adds those labels.

Example:
{"acceptance_criteria": [{"story_ref": "As a Visitor...", "given": "a visitor on the registration page", "when": "they submit a valid registration form", "then": "they receive a confirmation email"}]}

Now generate criteria for the following user stories.
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


_LABEL_RE = re.compile(r"^\s*(given|when|then|and)\b[\s,:\-]*", re.IGNORECASE)


def _strip_label(value) -> str:
    """Remove a leading Given/When/Then label so the UI can add it once."""
    text = str(value if value is not None else "").strip()
    return _LABEL_RE.sub("", text, count=1).strip()


def _dedupe_acceptance_criteria(criteria: List[Dict]) -> List[Dict]:
    seen = set()
    out = []
    for c in criteria:
        story_ref = str(c.get("story_ref", "")).strip()
        given = _strip_label(c.get("given", ""))
        when = _strip_label(c.get("when", ""))
        then = _strip_label(c.get("then", ""))
        key = (story_ref.lower(), given.lower(), when.lower(), then.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "story_ref": story_ref,
            "given": given,
            "when": when,
            "then": then,
        })
    return out


BATCH_SIZE = 8  # stories per LLM call; keeps responses short enough to parse


def _criteria_for_batch(stories: List[Dict], raw: str, errors: List[str]) -> List[Dict]:
    prompt = PROMPT + json.dumps({"user_stories": stories}, indent=2) + "\nDocument:\n" + raw
    for _ in range(2):
        try:
            parsed = _extract_json(_call_groq(prompt))
            normalized = []
            for c in parsed.get("acceptance_criteria", []) or []:
                c = c if isinstance(c, dict) else {}
                normalized.append({
                    "story_ref": c.get("story_ref"),
                    "given": c.get("given"),
                    "when": c.get("when"),
                    "then": c.get("then"),
                })
            return normalized
        except Exception as e:
            errors.append(str(e))
            time.sleep(1)
    return []


def generate_acceptance_criteria(state: Dict) -> Dict:
    stories: List[Dict] = state.get("user_stories", []) or []
    raw = state.get("raw_text", "")
    errors: List[str] = []
    collected: List[Dict] = []
    for i in range(0, len(stories), BATCH_SIZE):
        batch_errors: List[str] = []
        got = _criteria_for_batch(stories[i:i + BATCH_SIZE], raw, batch_errors)
        if got:
            collected.extend(got)  # a retry that succeeded is not an error
        else:
            errors.extend(batch_errors)
    result = {"acceptance_criteria": _dedupe_acceptance_criteria(collected)}
    if errors:
        result["errors"] = errors
    return result


if __name__ == "__main__":
    state = {"user_stories": [{"story": "As a Visitor, I want to register with email so that I can place orders"}]}
    print(generate_acceptance_criteria(state))
