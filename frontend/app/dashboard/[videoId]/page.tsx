"use client";

import { useParams } from "next/navigation";
import { Loader2, AlertTriangle, Film } from "lucide-react";
import { useVideoDashboard } from "@/hooks/useVideoDashboard";
import { TimelineViewer } from "@/components/TimelineViewer";
import { DNAViewer } from "@/components/DNAViewer";
import { GenerationPanel } from "@/components/GeneratedContentPanel";
import { HistoryPanel } from "@/components/HistoryPanel";
import { Card, CardContent } from "@/components/ui/card";
import { formatDuration } from "@/lib/utils";

export default function DashboardPage() {
  const params = useParams<{ videoId: string }>();
  const { video, dna, loading, analyzing, error, generations, generate, generating } =
    useVideoDashboard(params.videoId);

  if (loading && !video) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-24 flex flex-col items-center gap-3 text-muted">
        <Loader2 className="h-6 w-6 animate-spin" />
        <p className="text-sm">Loading video…</p>
      </div>
    );
  }

  if (error && !video) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-24 flex flex-col items-center gap-3 text-danger">
        <AlertTriangle className="h-6 w-6" />
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex items-center gap-3 mb-8">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-surface-raised border border-border">
          <Film className="h-4 w-4 text-primary" />
        </div>
        <div>
          <h1 className="font-display text-xl font-semibold">{video?.filename}</h1>
          <p className="text-xs text-muted font-mono">
            {formatDuration(video?.duration_seconds ?? undefined)} ·{" "}
            {video?.size_bytes ? (video.size_bytes / (1024 * 1024)).toFixed(1) : "—"} MB ·{" "}
            {video?.status}
          </p>
        </div>
      </div>

      {analyzing && (
        <Card className="mb-6">
          <CardContent className="flex items-center gap-3 py-4">
            <Loader2 className="h-4 w-4 animate-spin text-accent" />
            <p className="text-sm text-muted">
              Running the Understanding Engine — extracting Content DNA…
            </p>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="mb-6 border-danger/40">
          <CardContent className="py-4 text-sm text-danger">{error}</CardContent>
        </Card>
      )}

      {dna && (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <DNAViewer dna={dna} />
            <TimelineViewer timeline={dna.timeline} />
          </div>
          <div className="lg:col-span-1">
            <GenerationPanel onGenerate={generate} generating={generating} latestResult={generations[0] ?? null} />
          </div>
          <div className="lg:col-span-1">
            <HistoryPanel generations={generations} />
          </div>
        </div>
      )}
    </div>
  );
}
