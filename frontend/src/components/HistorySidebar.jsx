import React from "react";

function label(run) {
  const name = (run.filename || "").split("/").pop() || `Run ${run.id}`;
  const when = run.created_at ? new Date(run.created_at + "Z").toLocaleString() : "";
  return { name, when };
}

export default function HistorySidebar({ runs = [], activeId = null, onSelect = () => {} }) {
  return (
    <aside className="rounded-xl border border-slate-200 bg-white p-4 lg:sticky lg:top-6 lg:self-start">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">History</h2>
      {runs.length === 0 ? (
        <p className="text-sm text-slate-400">No past runs yet.</p>
      ) : (
        <ul className="max-h-[70vh] space-y-1 overflow-y-auto">
          {runs.map((run) => {
            const { name, when } = label(run);
            const active = run.id === activeId;
            return (
              <li key={run.id}>
                <button
                  type="button"
                  onClick={() => onSelect(run.id)}
                  className={
                    "w-full rounded-lg px-3 py-2 text-left text-sm transition " +
                    (active ? "bg-indigo-50 text-indigo-700" : "hover:bg-slate-100")
                  }
                >
                  <div className="truncate font-medium">{name}</div>
                  <div className="text-xs text-slate-500">#{run.id} · {when}</div>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </aside>
  );
}
