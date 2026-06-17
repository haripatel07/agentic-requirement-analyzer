from backend import db


def test_db_can_save_and_load_runs(tmp_path):
    db_path = tmp_path / "runs.db"

    db.init_db(str(db_path))
    run_id = db.save_run("sample.txt", {"report": "ok"}, str(db_path))

    runs = db.list_runs(str(db_path))
    loaded = db.get_run(run_id, str(db_path))

    assert len(runs) == 1
    assert runs[0]["filename"] == "sample.txt"
    assert loaded is not None
    assert loaded["id"] == run_id
    assert loaded["report"] == {"report": "ok"}
