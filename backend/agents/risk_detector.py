"""Agent 6 — Risk & Ambiguity Detection

detect_risks_ambiguity(state: dict) -> dict
"""
import os
import json
import time
import re
from typing import Dict, List, Tuple

# Seed corpus of ambiguous phrases with reasons
SEED_CORPUS = [
    ("quickly", "vague performance requirement, needs measurable metric"),
    ("user-friendly", "subjective UX term; needs concrete success criteria"),
    ("as needed", "unclear trigger or frequency"),
    ("should support", "unspecified scope of support"),
    ("scalable", "no target scale or SLA specified"),
]

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    _embeddings = _embed_model.encode([p for p, _ in SEED_CORPUS])
    _faiss_index = faiss.IndexFlatIP(_embeddings.shape[1])
    import numpy as np
    _faiss_index.add(np.array(_embeddings))
except Exception:
    _embed_model = None
    _faiss_index = None


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


def detect_risks_ambiguity(state: Dict) -> Dict:
    items = list(state.get("functional_requirements", []) or []) + list(state.get("non_functional_requirements", []) or [])
    risks = []
    ambiguities = []
    errors = []
    for req in items:
        matched: List[Tuple[str, str, float]] = []
        if _embed_model and _faiss_index is not None:
            try:
                vec = _embed_model.encode([req])[0]
                import numpy as np
                D, I = _faiss_index.search(np.array([vec]), k=3)
                for score, idx in zip(D[0], I[0]):
                    if idx < 0:
                        continue
                    phrase, reason = SEED_CORPUS[int(idx)]
                    matched.append((phrase, reason, float(score)))
            except Exception as e:
                errors.append(str(e))
        # If matched high-similarity seeds, call LLM to confirm and suggest
        if matched:
            top = matched[0]
            seed_phrase, seed_reason, score = top
            prompt = (
                f"The requirement is: '{req}'. It matches an ambiguous seed phrase "
                f"'{seed_phrase}' because: {seed_reason}. Suggest a concrete suggestion "
                f"to resolve this ambiguity. Return JSON with keys requirement, reason, "
                f"and suggestion."
            )
            try:
                resp = _call_groq(prompt)
                parsed = _extract_json(resp)
                ambiguities.append(parsed)
            except Exception as e:
                errors.append(str(e))
        else:
            # optional lightweight heuristic: flag common vague words
            lowered = req.lower()
            for phrase, reason in SEED_CORPUS:
                if phrase in lowered:
                    ambiguities.append({"requirement": req, "reason": reason, "suggestion": "Specify measurable criteria (e.g., 'response time < 2s')"})
                    break

    return {"risks": risks, "ambiguities": ambiguities, "errors": errors}


if __name__ == "__main__":
    state = {"functional_requirements": ["Images should load quickly"], "non_functional_requirements": ["System should be scalable"]}
    print(detect_risks_ambiguity(state))
