import { History as HistoryIcon } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { CopyButton } from "@/components/CopyButton";
import type { GenerationResult } from "@/types";
import { formatTimestamp, titleCase } from "@/lib/utils";

export function HistoryPanel({ generations }: { generations: GenerationResult[] }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2">
        <HistoryIcon className="h-4 w-4 text-accent" />
        <CardTitle>History</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {generations.length === 0 ? (
          <p className="text-sm text-muted">Nothing generated yet.</p>
        ) : (
          generations.map((g) => (
            <div key={g.id} className="rounded-xl border border-border p-3">
              <div className="flex items-center justify-between mb-1.5">
                <p className="text-xs font-mono text-accent">
                  {titleCase(g.purpose)} · {titleCase(g.platform)} · {titleCase(g.persona)}
                </p>
                <CopyButton text={g.content} />
              </div>
              <p className="text-sm text-muted line-clamp-3">{g.content}</p>
              <p className="text-[11px] text-muted mt-2 font-mono">{formatTimestamp(g.created_at)}</p>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
