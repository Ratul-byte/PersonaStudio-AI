import { Clock } from "lucide-react";
import type { TimelineEvent } from "@/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { formatDuration } from "@/lib/utils";

export function TimelineViewer({ timeline }: { timeline: TimelineEvent[] }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2">
        <Clock className="h-4 w-4 text-accent" />
        <CardTitle>Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        {timeline.length === 0 ? (
          <p className="text-sm text-muted">No notable timestamps were detected.</p>
        ) : (
          <ol className="relative border-l border-border ml-1.5 space-y-5">
            {timeline.map((event, i) => (
              <li key={i} className="ml-4">
                <span className="absolute -left-[5px] mt-1.5 h-2.5 w-2.5 rounded-full bg-primary" />
                <span className="font-mono text-xs text-accent">
                  {formatDuration(event.timestamp_seconds)}
                </span>
                <p className="text-sm mt-0.5">{event.label}</p>
              </li>
            ))}
          </ol>
        )}
      </CardContent>
    </Card>
  );
}
