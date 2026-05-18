import { useEffect, useState, type ReactNode } from "react";
import { Badge } from "@/ui/badge";
import { Train } from "lucide-react";

type Health = {
  status: string;
  voice_provider?: string;
};

export function Header(): ReactNode {
  const [health, setHealth] = useState<Health | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/health")
      .then((r) => (r.ok ? (r.json() as Promise<Health>) : null))
      .then((data) => {
        if (!cancelled) setHealth(data);
      })
      .catch(() => {
        if (!cancelled) setHealth(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const providerLabel =
    health?.voice_provider === "speech_services"
      ? "Powered by Azure Speech Services"
      : "Powered by Foundry Realtime";

  return (
    <header className="flex items-center justify-between bg-subway-blue text-white px-6 py-3 shadow-md">
      <div className="flex items-center gap-3">
        <Train className="h-6 w-6 text-subway-yellow" aria-hidden />
        <h1 className="text-lg font-semibold">MTA Hackathon — Crosstown App</h1>
      </div>
      <Badge tone="yellow" data-testid="provider-badge">
        {providerLabel}
      </Badge>
    </header>
  );
}
