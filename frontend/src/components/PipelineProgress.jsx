import React from "react";

export default function PipelineProgress({step=0}){
  const steps = ["Uploading","Parsing+Analysis","Generating report"];
  return (
    <div className="p-3 border rounded bg-white">
      <div className="text-sm font-medium mb-2">Pipeline Progress</div>
      <ul className="space-y-1">
        {steps.map((s,i)=> (
          <li key={s} className={"flex items-center " + (i+1===step?"font-semibold":"text-gray-600")}>
            <span className="w-6 inline-block">{i+1===step? '●' : i+1 < step ? '✓' : '○'}</span>
            <span>{s}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
