from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from .graph import run_pipeline_partial, run_pipeline_full
from . import db
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pathlib import Path

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


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    dest = UPLOAD_DIR / file.filename
    try:
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    finally:
        await file.close()
    return {"filename": str(dest), "status": "uploaded"}



class AnalyzeRequest(BaseModel):
    filename: str


@app.post("/analyze/step1")
def analyze_step1(req: AnalyzeRequest):
    # Expects a filename returned from /upload
    filename = req.filename
    if not filename:
        return {"error": "filename required"}
    result = run_pipeline_partial(filename)
    return result


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    filename = req.filename
    if not filename:
        return {"error": "filename required"}
    # ensure DB
    db.init_db()
    res = run_pipeline_full(filename)
    report = res.get("report")
    run_id = db.save_run(filename, report)
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
        return {"error": "not found"}
    return r
