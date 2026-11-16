"""Assemble final report from PipelineState."""
import os
import json
import time
from typing import Dict


def _call_groq_for_summary(text: str) -> str:
    try:
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return ""
        client = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=api_key,
        )
        prompt = f"Summarize the following requirements document in 2-3 sentences:\n\n{text}"
        resp = client.invoke(prompt)
        if hasattr(resp, "content"):
            return resp.content
        return str(resp)
    except Exception:
        return ""


def assemble_report(state: Dict) -> Dict:
    summary = _call_groq_for_summary(state.get("raw_text", ""))
    report = {
        "executive_summary": summary,
        "functional_requirements": state.get("functional_requirements", []),
        "non_functional_requirements": state.get("non_functional_requirements", []),
        "user_stories": state.get("user_stories", []),
        "acceptance_criteria": state.get("acceptance_criteria", []),
        "risks": state.get("risks", []),
        "ambiguities": state.get("ambiguities", []),
        "suggestions": [],
        "errors": state.get("errors", []),
    }
    # Aggregate suggestions from ambiguities/risks
    suggestions = []
    seen = set()
    for a in report["ambiguities"]:
        s = a.get("suggestion") or ""
        key = s.strip().lower()
        if s and key not in seen:
            seen.add(key)
            suggestions.append(s)
    for r in report["risks"]:
        s = r.get("suggestion") or ""
        key = s.strip().lower()
        if s and key not in seen:
            seen.add(key)
            suggestions.append(s)
    report["suggestions"] = suggestions
    return report


if __name__ == "__main__":
    sample_state = {"raw_text": "A short doc about ShopQuick e-commerce platform."}
    print(assemble_report(sample_state))
