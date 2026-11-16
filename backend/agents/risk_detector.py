"""Agent 6 — Risk & Ambiguity Detection

detect_risks_ambiguity(state: dict) -> dict
"""
import os
import json
import re
from typing import Dict, List, Tuple

# Seed corpus of ambiguous phrases with reasons
SEED_CORPUS = [
    ("quickly", "vague performance requirement, needs measurable metric"),
    ("fast", "vague performance requirement, needs measurable metric"),
    ("user-friendly", "subjective UX term; needs concrete success criteria"),
    ("intuitive", "subjective UX term; needs concrete success criteria"),
    ("as needed", "unclear trigger or frequency"),
    ("should support", "unspecified scope of support"),
    ("scalable", "no target scale or SLA specified"),
    ("acceptable", "unclear quality threshold"),
    ("minimal downtime", "unclear availability target without SLA"),
]

SIMILARITY_THRESHOLD = 0.40
MAX_MATCHES_PER_REQUIREMENT = 2
MAX_AMBIGUITIES_PER_RUN = 12
MAX_RISKS_PER_RUN = 10
VAGUE_PATTERN = re.compile(
    r"\b(quickly|fast|user-?friendly|intuitive|as needed|should support|"
    r"scalable|acceptable|minimal downtime|responsive|efficient|secure)\b",
    flags=re.IGNORECASE,
)

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    _embeddings = _embed_model.encode(
        [p for p, _ in SEED_CORPUS],
        normalize_embeddings=True,
    )
    _faiss_index = faiss.IndexFlatIP(_embeddings.shape[1])
    import numpy as np
    _faiss_index.add(np.asarray(_embeddings, dtype="float32"))
except Exception:
    _embed_model = None
    _faiss_index = None


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


def _keyword_hits(requirement: str) -> List[str]:
    lowered = requirement.lower()
    hits = []
    for phrase, _ in SEED_CORPUS:
        if phrase in lowered:
            hits.append(phrase)
    for match in VAGUE_PATTERN.findall(requirement):
        term = match.lower()
        if term not in hits:
            hits.append(term)
    return hits


def _heuristic_ambiguity(requirement: str, phrase: str) -> Dict:
    reason = "unclear requirement wording; provide measurable criteria"
    for p, r in SEED_CORPUS:
        if p == phrase:
            reason = r
            break
    return {
        "requirement": requirement,
        "reason": reason,
        "suggestion": "Specify measurable criteria (e.g., response time, throughput, SLA, or clear trigger conditions).",
    }


# Delivery / operational risk categories: (category, keywords, severity, mitigation)
RISK_RULES = [
    ("Security", ("password", "payment", "authenticat", "login", "encrypt", "personal data", "pii", "secure"),
     "High", "Define authentication, encryption and access-control requirements and schedule a security review."),
    ("Compliance", ("hipaa", "gdpr", "compliance", "audit", "regulat", "patient", "medical", "payroll"),
     "High", "Identify applicable regulations early and add traceable compliance acceptance criteria."),
    ("Integration", ("integrat", "third-party", "third party", "api", "gateway", "external", "import", "sync"),
     "Medium", "Document interface contracts and add fallback behaviour for external-service failures."),
    ("Performance", ("concurrent", "real-time", "real time", "thousand", "million", "peak", "throughput"),
     "Medium", "Set measurable throughput and latency targets and plan load testing."),
    ("Data", ("migrat", "backup", "retention", "legacy", "report", "analytics"),
     "Medium", "Define data ownership, backup and migration approach before development."),
]


def _detect_risks(items: List[str]) -> List[Dict]:
    """Rule-based delivery/operational risks, one per (requirement, category)."""
    found = []
    for req in items:
        text = str(req).strip()
        lowered = text.lower()
        if not text:
            continue
        for category, keywords, severity, mitigation in RISK_RULES:
            if any(k in lowered for k in keywords):
                found.append({
                    "requirement": text,
                    "reason": f"{category} risk ({severity}): requirement touches {category.lower()}-sensitive behaviour.",
                    "suggestion": mitigation,
                })
                break
    return found[:MAX_RISKS_PER_RUN]


def detect_risks_ambiguity(state: Dict) -> Dict:
    items = list(state.get("functional_requirements", []) or []) + list(state.get("non_functional_requirements", []) or [])
    risks = _detect_risks(items)
    ambiguities_with_score = []
    errors = []

    for req in items:
        req = str(req).strip()
        if not req:
            continue

        keyword_hits = _keyword_hits(req)
        if not keyword_hits:
            continue

        matched: List[Tuple[str, str, float]] = []
        if _embed_model and _faiss_index is not None:
            try:
                vec = _embed_model.encode([req], normalize_embeddings=True)[0]
                import numpy as np
                k = min(5, len(SEED_CORPUS))
                D, I = _faiss_index.search(np.asarray([vec], dtype="float32"), k=k)
                for score, idx in zip(D[0], I[0]):
                    if idx < 0:
                        continue
                    phrase, reason = SEED_CORPUS[int(idx)]
                    score = float(score)
                    if score >= SIMILARITY_THRESHOLD:
                        matched.append((phrase, reason, score))
            except Exception as e:
                errors.append(str(e))

        matched.sort(key=lambda x: x[2], reverse=True)
        matched = matched[:MAX_MATCHES_PER_REQUIREMENT]

        if matched:
            seed_phrase, seed_reason, score = matched[0]
            prompt = (
                f"The requirement is: '{req}'. It matches an ambiguous seed phrase "
                f"'{seed_phrase}' because: {seed_reason}. Suggest a concrete suggestion "
                f"to resolve this ambiguity. Return JSON with keys requirement, reason, "
                f"and suggestion."
            )
            try:
                resp = _call_groq(prompt)
                parsed = _extract_json(resp)
                if not isinstance(parsed, dict):
                    raise ValueError("Model response JSON is not an object")
                parsed["requirement"] = str(parsed.get("requirement") or req).strip()
                parsed["reason"] = str(parsed.get("reason") or seed_reason).strip()
                parsed["suggestion"] = str(parsed.get("suggestion") or _heuristic_ambiguity(req, seed_phrase)["suggestion"]).strip()
                parsed["_score"] = score
                ambiguities_with_score.append(parsed)
            except Exception as e:
                errors.append(str(e))
                heuristic = _heuristic_ambiguity(req, seed_phrase)
                heuristic["_score"] = score
                ambiguities_with_score.append(heuristic)
        else:
            phrase = keyword_hits[0]
            heuristic = _heuristic_ambiguity(req, phrase)
            heuristic["_score"] = 0.0
            ambiguities_with_score.append(heuristic)

    # Keep only the strongest ambiguity candidates for cleaner reports.
    ambiguities_with_score.sort(key=lambda x: float(x.get("_score", 0.0)), reverse=True)

    ambiguities = []
    seen_requirements = set()
    for item in ambiguities_with_score:
        requirement_key = str(item.get("requirement", "")).strip().lower()
        if not requirement_key or requirement_key in seen_requirements:
            continue
        seen_requirements.add(requirement_key)
        ambiguities.append(
            {
                "requirement": item.get("requirement", ""),
                "reason": item.get("reason", ""),
                "suggestion": item.get("suggestion", ""),
            }
        )
        if len(ambiguities) >= MAX_AMBIGUITIES_PER_RUN:
            break

    return {"risks": risks, "ambiguities": ambiguities, "errors": errors}


if __name__ == "__main__":
    state = {"functional_requirements": ["Images should load quickly"], "non_functional_requirements": ["System should be scalable"]}
    print(detect_risks_ambiguity(state))
