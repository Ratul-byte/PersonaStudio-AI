import { Dna } from "lucide-react";
import type { ContentDNA } from "@/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function TagRow({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="text-xs font-mono uppercase tracking-wider text-muted mb-1.5">{label}</p>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item) => (
          <Badge key={item}>{item}</Badge>
        ))}
      </div>
    </div>
  );
}

export function DNAViewer({ dna }: { dna: ContentDNA }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2">
        <Dna className="h-4 w-4 text-accent" />
        <CardTitle>Content DNA</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div>
          <h4 className="font-display text-base font-semibold mb-1">{dna.title}</h4>
          <p className="text-sm text-muted leading-relaxed">{dna.summary}</p>
        </div>

        <div className="rounded-xl bg-surface-raised/60 border border-border p-3">
          <p className="text-xs font-mono uppercase tracking-wider text-accent mb-1">
            Core message
          </p>
          <p className="text-sm">{dna.core_message || "—"}</p>
        </div>

        <div className="flex gap-2 flex-wrap">
          <Badge className="border-primary/40 text-primary">tone: {dna.tone}</Badge>
          <Badge className="border-accent/40 text-accent">sentiment: {dna.sentiment}</Badge>
        </div>

        <TagRow label="Topics" items={dna.topics} />
        <TagRow label="Keywords" items={dna.keywords} />
        <TagRow label="Entities" items={dna.entities} />
        <TagRow label="Key events" items={dna.key_events} />
        <TagRow label="People" items={dna.people} />
        <TagRow label="Activities" items={dna.activities} />
        <TagRow label="Detected objects" items={dna.detected_objects} />

        {dna.context && (
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-muted mb-1.5">Context</p>
            <p className="text-sm text-muted leading-relaxed">{dna.context}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
