import { useState, type ReactNode } from "react";
import type { ToolCallEntry } from "@/hooks/useVoiceSession";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/card";
import { Badge } from "@/ui/badge";
import { ChevronDown, ChevronRight, Wrench } from "lucide-react";

export function ToolCallPanel({ entries }: { entries: ToolCallEntry[] }): ReactNode {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wrench className="h-4 w-4" /> Tool calls
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {entries.length === 0 ? (
          <p className="text-sm text-slate-400 italic">
            Tool calls and citations appear here.
          </p>
        ) : (
          entries.map((e) => <ToolCallRow key={e.call_id} entry={e} />)
        )}
      </CardContent>
    </Card>
  );
}

function ToolCallRow({ entry }: { entry: ToolCallEntry }): ReactNode {
  const [open, setOpen] = useState(true);
  return (
    <div className="rounded-md border border-slate-200">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-3 py-2 text-left text-sm font-medium"
      >
        <span className="flex items-center gap-2">
          {open ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
          {entry.name}
        </span>
        {entry.pending ? (
          <Badge tone="muted">running…</Badge>
        ) : (
          <Badge tone="default">{(entry.citations ?? []).length} cites</Badge>
        )}
      </button>
      {open && (
        <div className="border-t border-slate-100 px-3 py-2 text-xs">
          <pre className="overflow-x-auto rounded bg-slate-50 p-2 text-[11px]">
            {JSON.stringify(entry.args, null, 2)}
          </pre>
          {(entry.citations ?? []).length > 0 && (
            <ul className="mt-2 space-y-1">
              {(entry.citations ?? []).map((c, i) => (
                <li key={i} className="text-slate-700">
                  <span className="font-mono text-[11px] text-subway-blue">
                    {String(c?.source ?? c?.url ?? `cite-${i}`)}
                  </span>
                  {c?.snippet ? `: ${c.snippet}` : null}
                </li>
              ))}
            </ul>
          )}
          {(entry.warnings ?? []).length > 0 && (
            <ul className="mt-2 list-disc pl-5 text-amber-700">
              {(entry.warnings ?? []).map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
