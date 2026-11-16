from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from .graph import run_pipeline_partial, run_pipeline_full
from . import db
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uuid
from pathlib import Path

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        await file.close()
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext or 'none'}")
    # Server-generated name: never trust the client-supplied path/filename.
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    size = 0
    try:
        with dest.open("wb") as f:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    f.close()
                    dest.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="File too large (max 5 MB)")
                f.write(chunk)
    finally:
        await file.close()
    return {"filename": str(dest), "status": "uploaded"}



class AnalyzeRequest(BaseModel):
    filename: str
    display_name: str | None = None


def _checked_path(filename: str) -> str:
    """Only files inside the upload directory may be analyzed."""
    if not filename:
        raise HTTPException(status_code=400, detail="filename required")
    resolved = Path(filename).resolve()
    if UPLOAD_DIR.resolve() not in resolved.parents:
        raise HTTPException(status_code=400, detail="filename must be an uploaded file")
    return str(resolved)


@app.post("/analyze/step1")
def analyze_step1(req: AnalyzeRequest):
    # Expects a filename returned from /upload
    filename = _checked_path(req.filename)
    result = run_pipeline_partial(filename)
    return result


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    filename = _checked_path(req.filename)
    # ensure DB
    db.init_db()
    res = run_pipeline_full(filename)
    report = res.get("report")
    run_id = db.save_run((req.display_name or Path(filename).name)[:200], report)
    return {"run_id": run_id, "report": report}


@app.get("/runs")
def list_runs():
    db.init_db()
    return {"runs": db.list_runs()}


@app.get("/runs/{run_id}")
def get_run(run_id: int):
    db.init_db()
    r = db.get_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="run not found")
    return r
