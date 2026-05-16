import { type ReactNode } from "react";
import type { ToolCallEntry } from "@/hooks/useVoiceSession";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/card";

export function AlternateRouteCard({
  entries,
}: {
  entries: ToolCallEntry[];
}): ReactNode {
  const relevant = entries.find(
    (e) =>
      !e.pending &&
      (e.name === "find_alternate_route" || e.name === "get_shuttle_bridging"),
  );
  if (!relevant) return null;
  const args = relevant.args as {
    origin?: unknown;
    destination?: unknown;
    disruption_id?: unknown;
    station?: unknown;
  };
  const origin = typeof args.origin === "string" ? args.origin : undefined;
  const destination =
    typeof args.destination === "string" ? args.destination : undefined;
  const disruptionId =
    typeof args.disruption_id === "string" ? args.disruption_id : undefined;
  const station = typeof args.station === "string" ? args.station : undefined;
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">
          {relevant.name === "find_alternate_route"
            ? "Suggested alternate route"
            : "Shuttle bridging"}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        {origin && destination && (
          <p>
            <span className="font-medium">{origin}</span> →{" "}
            <span className="font-medium">{destination}</span>
          </p>
        )}
        {station && (
          <p>
            Station: <span className="font-medium">{station}</span>
          </p>
        )}
        {disruptionId && (
          <p className="font-mono text-xs text-slate-500">{disruptionId}</p>
        )}
        {relevant.citations.length > 0 && (
          <ul className="text-xs text-slate-600">
            {relevant.citations.map((c, i) => {
              const id = typeof c.id === "string" ? c.id : `cite-${i}`;
              return (
                <li key={id}>
                  <span className="font-mono">{id}</span>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
