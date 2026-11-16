import React from "react";

const STEPS = ["Uploading", "Running agent pipeline", "Assembling report"];

export default function PipelineProgress({ step = 0 }) {
  return (
    <ol className="flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-white p-4 text-sm" aria-label="Pipeline progress">
      {STEPS.map((s, i) => {
        const n = i + 1;
        const state = n === step ? "active" : n < step ? "done" : "todo";
        return (
          <li
            key={s}
            data-state={state}
            className={
              "flex items-center gap-2 rounded-full px-3 py-1 " +
              (state === "active"
                ? "bg-indigo-600 font-semibold text-white"
                : state === "done"
                ? "bg-emerald-100 text-emerald-700"
                : "bg-slate-100 text-slate-500")
            }
          >
            <span aria-hidden="true">{state === "done" ? "✓" : n}</span>
            <span>{s}</span>
            {state === "active" && (
              <span className="h-3 w-3 animate-spin rounded-full border-2 border-white border-t-transparent" aria-hidden="true" />
            )}
          </li>
        );
      })}
    </ol>
  );
}
