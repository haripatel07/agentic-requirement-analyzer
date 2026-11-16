import React, { useCallback, useEffect, useState } from "react";
import UploadForm from "./components/UploadForm";
import ReportView from "./components/ReportView";
import HistorySidebar from "./components/HistorySidebar";
import { getRun, listRuns } from "./api";

export default function App() {
  const [report, setReport] = useState(null);
  const [runs, setRuns] = useState([]);
  const [activeRun, setActiveRun] = useState(null);

  const refreshRuns = useCallback(async () => {
    try {
      const data = await listRuns();
      setRuns((data && data.runs) || []);
    } catch {
      setRuns([]);
    }
  }, []);

  useEffect(() => {
    refreshRuns();
  }, [refreshRuns]);

  const handleComplete = (result) => {
    setReport(result.report);
    setActiveRun(result.run_id ?? null);
    refreshRuns();
  };

  const openRun = async (id) => {
    try {
      const run = await getRun(id);
      if (run && run.report) {
        setReport(run.report);
        setActiveRun(id);
      }
    } catch {
      /* ignore: sidebar stays on current report */
    }
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-6 py-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-lg font-bold text-white">A</div>
          <div>
            <h1 className="text-lg font-semibold leading-tight">Agentic Requirement Analyzer</h1>
            <p className="text-xs text-slate-500">Requirement documents to user stories, acceptance criteria and risk flags</p>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[17rem_1fr]">
        <HistorySidebar runs={runs} activeId={activeRun} onSelect={openRun} />
        <div className="min-w-0 space-y-6">
          <UploadForm onComplete={handleComplete} />
          {report && <ReportView report={report} />}
        </div>
      </main>
    </div>
  );
}
