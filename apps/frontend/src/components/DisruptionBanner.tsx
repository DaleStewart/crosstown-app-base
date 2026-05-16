import { type ReactNode } from "react";
import type { ToolCallEntry } from "@/hooks/useVoiceSession";

type LineStatus = {
  line: string;
  status: string;
  disruption_id: string | null;
  summary: string | null;
};

function extractStatuses(entries: ToolCallEntry[]): LineStatus[] {
  const byLine = new Map<string, LineStatus>();
  for (const e of entries) {
    if (e.name !== "get_disruption_status") continue;
    // Skip pending calls — they have no citations yet and would incorrectly
    // overwrite a previously settled (active) status with "operating_normally".
    if (e.pending) continue;
    const args = e.args as { line?: unknown };
    const line = typeof args.line === "string" ? args.line.toUpperCase() : "";
    if (!line) continue;
    // Prefer the most recent / non-pending entry per line.
    const incidentCite = e.citations.find((c) => c.type === "incident");
    const incId = typeof incidentCite?.id === "string" ? incidentCite.id : null;
    const incSnippet =
      typeof incidentCite?.snippet === "string" ? incidentCite.snippet : null;
    const status: LineStatus = {
      line,
      status: incidentCite ? "active" : "operating_normally",
      disruption_id: incId,
      summary: incSnippet,
    };
    byLine.set(line, status);
  }
  return Array.from(byLine.values());
}

export function DisruptionBanner({
  entries,
}: {
  entries: ToolCallEntry[];
}): ReactNode {
  const statuses = extractStatuses(entries);
  if (statuses.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2 rounded-md border border-slate-200 bg-white p-3">
      {statuses.map((s) => {
        const active = s.status === "active";
        return (
          <div
            key={s.line}
            className={
              "flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium " +
              (active
                ? "bg-red-100 text-red-800"
                : "bg-emerald-100 text-emerald-800")
            }
          >
            <span className="font-bold">{s.line}</span>
            <span>{active ? "service disruption" : "operating normally"}</span>
            {s.disruption_id && (
              <span className="rounded bg-white/60 px-1 font-mono text-[10px]">
                {s.disruption_id}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
