from pathlib import Path

from backend.agents.parser import parse_document


def test_parse_document_reads_and_cleans_txt(tmp_path: Path):
    doc = tmp_path / "sample.txt"
    doc.write_text("Hello   world\n\nThis is\ta test.\n", encoding="utf-8")

    result = parse_document({"filename": str(doc)})

    assert result["raw_text"] == "Hello   world\nThis is\ta test."
    assert "errors" not in result


def test_parse_document_returns_error_for_missing_file():
    result = parse_document({"filename": "/tmp/does-not-exist.txt"})

    assert result["raw_text"] == ""
    assert result["errors"] == ["file not found: /tmp/does-not-exist.txt"]
