"""Agent 1 — Document Parsing

Provides parse_document(state) -> dict
"""
from typing import Dict
from pathlib import Path


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
    except Exception:
        raise
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        raise
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def _clean_text(text: str) -> str:
    lines = [l.strip() for l in text.splitlines()]
    # remove empty lines and join with single newline
    return "\n".join([l for l in lines if l])


def parse_document(state: Dict) -> Dict:
    filename = state.get("filename", "")
    path = Path(filename)
    try:
        if not path.exists():
            return {"raw_text": "", "errors": [f"file not found: {filename}"]}
        ext = path.suffix.lower()
        if ext == ".txt":
            text = _read_txt(path)
        elif ext == ".docx":
            text = _read_docx(path)
        elif ext == ".pdf":
            text = _read_pdf(path)
        else:
            return {"raw_text": "", "errors": [f"unsupported file type: {ext}"]}
        cleaned = _clean_text(text)
        return {"raw_text": cleaned}
    except Exception as e:
        return {"raw_text": "", "errors": [str(e)]}


if __name__ == "__main__":
    # quick local test
    sample = Path(__file__).resolve().parents[2] / "sample_docs" / "sample_requirement.txt"
    state = {"filename": str(sample)}
    out = parse_document(state)
    print(out)
