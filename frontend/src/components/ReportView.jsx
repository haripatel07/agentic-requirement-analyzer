import React from "react";

const PRIORITY = {
  high: "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-emerald-100 text-emerald-700",
};

function Section({ title, count, children }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 flex items-center gap-2 text-base font-semibold">
        {title}
        {typeof count === "number" && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">{count}</span>
        )}
      </h3>
      {children}
    </section>
  );
}

function Empty() {
  return <p className="text-sm text-slate-400">None found.</p>;
}

function Bullets({ items }) {
  if (!items.length) return <Empty />;
  return (
    <ul className="list-disc space-y-1 pl-5 text-sm">
      {items.map((t, i) => (
        <li key={i}>{t}</li>
      ))}
    </ul>
  );
}

function Issues({ items, tone }) {
  if (!items.length) return <Empty />;
  const border = tone === "risk" ? "border-red-200 bg-red-50" : "border-amber-200 bg-amber-50";
  return (
    <ul className="space-y-3">
      {items.map((a, i) => (
        <li key={i} className={"rounded-lg border p-3 text-sm " + border}>
          <p className="font-medium">{a.requirement}</p>
          <p className="mt-1 text-slate-600">{a.reason}</p>
          <p className="mt-1"><span className="font-semibold">Suggestion:</span> {a.suggestion}</p>
        </li>
      ))}
    </ul>
  );
}

export function reportToMarkdown(rs) {
  const list = (a) => (a || []).map((x) => `- ${x}`).join("\n") || "_None_";
  const out = ["# Requirement Analysis Report", "", "## Executive Summary", rs.executive_summary || "—", ""];
  out.push("## Functional Requirements", list(rs.functional_requirements), "");
  out.push("## Non-Functional Requirements", list(rs.non_functional_requirements), "");
  out.push("## User Stories");
  (rs.user_stories || []).forEach((s) => out.push(`- **[${s.priority}]** ${s.story} _(${s.feature})_`));
  out.push("", "## Acceptance Criteria");
  (rs.acceptance_criteria || []).forEach((c) =>
    out.push(`- ${c.story_ref}\n  - Given ${c.given}\n  - When ${c.when}\n  - Then ${c.then}`)
  );
  out.push("", "## Risks");
  (rs.risks || []).forEach((r) => out.push(`- ${r.requirement} — ${r.reason} Suggestion: ${r.suggestion}`));
  out.push("", "## Ambiguities");
  (rs.ambiguities || []).forEach((a) => out.push(`- ${a.requirement} — ${a.reason} Suggestion: ${a.suggestion}`));
  return out.join("\n");
}

function download(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ReportView({ report }) {
  if (!report) return null;
  const rs = report;
  const fr = rs.functional_requirements || [];
  const nfr = rs.non_functional_requirements || [];
  const stories = rs.user_stories || [];
  const criteria = rs.acceptance_criteria || [];
  const ambiguities = rs.ambiguities || [];
  const risks = rs.risks || [];
  const suggestions = rs.suggestions || [];
  const errors = rs.errors || [];

  const stats = [
    ["Functional", fr.length],
    ["Non-functional", nfr.length],
    ["User stories", stories.length],
    ["Criteria sets", criteria.length],
    ["Ambiguities", ambiguities.length],
    ["Risks", risks.length],
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-xl font-bold">Analysis Report</h2>
        <div className="flex gap-2">
          <button type="button" onClick={() => download("report.md", reportToMarkdown(rs), "text/markdown")}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-100">Export Markdown</button>
          <button type="button" onClick={() => download("report.json", JSON.stringify(rs, null, 2), "application/json")}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-100">Export JSON</button>
        </div>
      </div>

      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {stats.map(([k, v]) => (
          <div key={k} className="rounded-xl border border-slate-200 bg-white p-3">
            <dt className="text-xs text-slate-500">{k}</dt>
            <dd className="text-2xl font-semibold text-indigo-600">{v}</dd>
          </div>
        ))}
      </dl>

      <Section title="Executive Summary">
        <p className="text-sm leading-relaxed">{rs.executive_summary || "—"}</p>
      </Section>

      <div className="grid gap-4 md:grid-cols-2">
        <Section title="Functional Requirements" count={fr.length}><Bullets items={fr} /></Section>
        <Section title="Non-Functional Requirements" count={nfr.length}><Bullets items={nfr} /></Section>
      </div>

      <Section title="User Stories" count={stories.length}>
        {stories.length === 0 ? <Empty /> : (
          <ul className="space-y-2">
            {stories.map((s, i) => (
              <li key={i} className="rounded-lg border border-slate-200 p-3 text-sm">
                <div className="flex items-start justify-between gap-3">
                  <p className="font-medium">{s.story}</p>
                  <span className={"shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold " + (PRIORITY[String(s.priority).toLowerCase()] || "bg-slate-100 text-slate-600")}>
                    {s.priority}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-500">Feature: {s.feature}</p>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Acceptance Criteria" count={criteria.length}>
        {criteria.length === 0 ? <Empty /> : (
          <ul className="space-y-3">
            {criteria.map((c, i) => (
              <li key={i} className="rounded-lg border border-slate-200 p-3 text-sm">
                <p className="mb-2 font-medium">{c.story_ref}</p>
                <dl className="grid grid-cols-[4rem_1fr] gap-x-3 gap-y-1">
                  <dt className="font-semibold text-indigo-600">Given</dt><dd>{c.given}</dd>
                  <dt className="font-semibold text-indigo-600">When</dt><dd>{c.when}</dd>
                  <dt className="font-semibold text-indigo-600">Then</dt><dd>{c.then}</dd>
                </dl>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <div className="grid gap-4 md:grid-cols-2">
        <Section title="Ambiguities" count={ambiguities.length}><Issues items={ambiguities} tone="ambiguity" /></Section>
        <Section title="Risks" count={risks.length}><Issues items={risks} tone="risk" /></Section>
      </div>

      <Section title="Suggestions" count={suggestions.length}><Bullets items={suggestions} /></Section>

      {errors.length > 0 && (
        <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <p className="font-semibold">Pipeline warnings</p>
          <ul className="list-disc pl-5">{errors.map((e, i) => <li key={i}>{String(e)}</li>)}</ul>
        </div>
      )}
    </div>
  );
}
