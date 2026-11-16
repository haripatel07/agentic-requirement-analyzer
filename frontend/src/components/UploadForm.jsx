import React, { useRef, useState } from "react";
import PipelineProgress from "./PipelineProgress";
import { analyze, uploadFile } from "../api";

const ACCEPTED = [".txt", ".pdf", ".docx"];

export default function UploadForm({ onComplete = () => {} }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState(false);
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(0);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const pick = (f) => {
    if (!f) return;
    const ok = ACCEPTED.some((ext) => f.name.toLowerCase().endsWith(ext));
    if (!ok) {
      setError(true);
      setStatus(`Unsupported file type. Use ${ACCEPTED.join(", ")}`);
      return;
    }
    setFile(f);
    setError(false);
    setStatus("");
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError(true);
      return setStatus("No file selected");
    }
    setError(false);
    setStatus("Uploading...");
    setRunning(true);
    setStep(1);
    try {
      const up = await uploadFile(file);
      setStatus("Analyzing requirements...");
      setStep(2);
      const result = await analyze(up.filename, file.name);
      if (result && result.error) throw new Error(result.error);
      setStep(3);
      setStatus("Analysis complete");
      onComplete(result);
    } catch (err) {
      setError(true);
      setStatus("Error: " + (err && err.message ? err.message : String(err)));
    } finally {
      setRunning(false);
      setStep(0);
    }
  };

  return (
    <section className="space-y-4">
      <form onSubmit={submit} className="rounded-xl border border-slate-200 bg-white p-5">
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); pick(e.dataTransfer.files[0]); }}
          onClick={() => inputRef.current && inputRef.current.click()}
          className={
            "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-8 text-center transition " +
            (dragging ? "border-indigo-500 bg-indigo-50" : "border-slate-300 hover:border-indigo-400")
          }
        >
          <p className="font-medium">{file ? file.name : "Drop a requirement document here"}</p>
          <p className="mt-1 text-sm text-slate-500">
            {file ? `${(file.size / 1024).toFixed(1)} KB` : "or click to browse · PDF, DOCX or TXT"}
          </p>
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED.join(",")}
            className="hidden"
            onChange={(e) => pick(e.target.files[0])}
          />
        </div>

        <div className="mt-4 flex items-center gap-4">
          <button
            type="submit"
            disabled={running}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Upload & Analyze
          </button>
          <span role="status" className={"text-sm " + (error ? "text-red-600" : "text-slate-600")}>
            {status}
          </span>
        </div>
      </form>

      {running && <PipelineProgress step={step} />}
    </section>
  );
}
