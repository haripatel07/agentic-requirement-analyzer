import React from "react";

export default function ReportView({report}){
  if(!report) return null;
  const rs = report;
  return (
    <div className="p-4 border rounded bg-white">
      <h2 className="text-xl font-bold mb-2">Executive Summary</h2>
      <p className="prose mb-4">{rs.executive_summary || '—'}</p>

      <h3 className="font-semibold">Functional Requirements</h3>
      <ul className="list-disc ml-6 mb-4">
        {(rs.functional_requirements || []).map((f,i)=>(<li key={i}>{f}</li>))}
      </ul>

      <h3 className="font-semibold">Non-Functional Requirements</h3>
      <ul className="list-disc ml-6 mb-4">
        {(rs.non_functional_requirements || []).map((f,i)=>(<li key={i}>{f}</li>))}
      </ul>

      <h3 className="font-semibold">User Stories</h3>
      <div className="mb-4">
        {(rs.user_stories || []).map((s,i)=>(
          <div key={i} className="p-2 border rounded mb-2">
            <div className="font-medium">{s.story}</div>
            <div className="text-sm text-gray-600">Feature: {s.feature} • Priority: {s.priority}</div>
          </div>
        ))}
      </div>

      <h3 className="font-semibold">Acceptance Criteria</h3>
      <ul className="ml-6 mb-4">
        {(rs.acceptance_criteria || []).map((c,i)=>(<li key={i}><strong>{c.story_ref}</strong>: Given {c.given} — When {c.when} — Then {c.then}</li>))}
      </ul>

      <h3 className="font-semibold">Ambiguities</h3>
      <ul className="ml-6 mb-4">
        {(rs.ambiguities || []).map((a,i)=>(<li key={i}>{a.requirement}: {a.reason} — Suggestion: {a.suggestion}</li>))}
      </ul>

      <h3 className="font-semibold">Suggestions</h3>
      <ul className="ml-6 mb-4">
        {(rs.suggestions || []).map((s,i)=>(<li key={i}>{s}</li>))}
      </ul>

      {(rs.errors && rs.errors.length>0) && (
        <div className="text-red-600">Errors: {JSON.stringify(rs.errors)}</div>
      )}
    </div>
  )
}
