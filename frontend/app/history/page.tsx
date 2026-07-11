"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";
import { api } from "@/services/api";
import { HistoryPanel } from "@/components/HistoryPanel";
import type { GenerationResult } from "@/types";

export default function HistoryPage() {
  const [generations, setGenerations] = React.useState<GenerationResult[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    api
      .getHistory()
      .then(setGenerations)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="font-display text-2xl font-semibold mb-2">History</h1>
      <p className="text-sm text-muted mb-8">Every piece of content generated across all videos.</p>

      {loading ? (
        <div className="flex items-center gap-2 text-muted text-sm">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading history…
        </div>
      ) : (
        <HistoryPanel generations={generations} />
      )}
    </div>
  );
}
