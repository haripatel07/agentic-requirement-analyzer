import React, {useState} from "react";
import PipelineProgress from "./PipelineProgress";
import ReportView from "./ReportView";

export default function UploadForm(){
  const [status, setStatus] = useState("");
  const [file, setFile] = useState(null);
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(0);
  const [report, setReport] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    if(!file) return setStatus("No file selected");
    setStatus('Uploading...');
    setRunning(true);
    setStep(1);
    const fd = new FormData();
    fd.append('file', file);
    try{
      const res = await fetch('http://localhost:8000/upload', {method: 'POST', body: fd});
      const json = await res.json();
      const filename = json.filename;
      setStatus('Uploaded');
      setStep(2);
      // call analyze
      const analyzeRes = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({filename})
      });
      setStep(3);
      const analyzeJson = await analyzeRes.json();
      if(analyzeJson.error){
        setStatus('Analyze error: ' + analyzeJson.error);
      } else {
        setStatus('Analysis complete');
        setReport(analyzeJson.report || analyzeJson);
      }
    }catch(err){
      setStatus('Error: ' + String(err));
    }finally{
      setRunning(false);
      setStep(0);
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="space-y-2">
        <input type="file" accept=".txt,.pdf,.docx" onChange={e=>setFile(e.target.files[0])} />
        <div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded" type="submit">Upload & Analyze</button>
        </div>
      </form>

      <div className="text-sm text-gray-600">{status}</div>

      {running && <PipelineProgress step={step} />}

      {report && <ReportView report={report} />}
    </div>
  )
}
