from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_endpoint_saves_file(tmp_path, monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr("backend.main.UPLOAD_DIR", tmp_path)

    response = client.post(
        "/upload",
        files={"file": ("sample.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    saved_path = Path(payload["filename"])
    assert payload["status"] == "uploaded"
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == "hello world"


def test_analyze_endpoint_uses_pipeline_and_db(tmp_path, monkeypatch):
    client = TestClient(app)

    fake_report = {"executive_summary": "ok", "functional_requirements": []}
    monkeypatch.setattr("backend.main.db.init_db", lambda *args, **kwargs: None)
    monkeypatch.setattr("backend.main.db.save_run", lambda filename, report: 99)
    monkeypatch.setattr("backend.main.run_pipeline_full", lambda filename: {"report": fake_report})

    response = client.post("/analyze", json={"filename": str(tmp_path / "doc.txt")})

    assert response.status_code == 200
    assert response.json() == {"run_id": 99, "report": fake_report}
