"""Assemble final report from PipelineState."""
import os
import json
import time
from typing import Dict


def _call_groq_for_summary(text: str) -> str:
    try:
        from langchain_groq import ChatGroq
        client = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"Summarize the following requirements document in 2-3 sentences:\n\n{text}"
        resp = client.chat([{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        if isinstance(resp, str):
            return resp
        if hasattr(resp, "content"):
            return resp.content
        if isinstance(resp, (list, tuple)) and len(resp) > 0:
            first = resp[0]
            return getattr(first, "content", str(first))
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
    for a in report["ambiguities"]:
        s = a.get("suggestion") or ""
        if s:
            suggestions.append(s)
    for r in report["risks"]:
        s = r.get("suggestion") or ""
        if s:
            suggestions.append(s)
    report["suggestions"] = suggestions
    return report


if __name__ == "__main__":
    sample_state = {"raw_text": "A short doc about ShopQuick e-commerce platform."}
    print(assemble_report(sample_state))
