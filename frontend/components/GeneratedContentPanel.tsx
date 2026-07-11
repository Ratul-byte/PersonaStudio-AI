"use client";

import * as React from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PersonaSelector } from "@/components/PersonaSelector";
import { PlatformSelector } from "@/components/PlatformSelector";
import { PurposeSelector } from "@/components/PurposeSelector";
import { ToneSelector, TONE_PRESETS } from "@/components/ToneSelector";
import { CopyButton } from "@/components/CopyButton";
import { DownloadButton } from "@/components/DownloadButton";
import { useToast } from "@/components/ui/toast";
import type { GenerationResult, Persona, Platform, Purpose, Tone } from "@/types";
import { titleCase } from "@/lib/utils";

interface GenerationPanelProps {
  onGenerate: (params: { persona: Persona; platform: Platform; purpose: Purpose; tone: Tone }) => Promise<GenerationResult | null>;
  generating: boolean;
  latestResult: GenerationResult | null;
}

export function GenerationPanel({ onGenerate, generating, latestResult }: GenerationPanelProps) {
  const [persona, setPersona] = React.useState<Persona>("developer");
  const [platform, setPlatform] = React.useState<Platform>("linkedin");
  const [purpose, setPurpose] = React.useState<Purpose>("caption");
  const [tone, setTone] = React.useState<Tone>("professional");
  const { push } = useToast();

  const handleGenerate = async () => {
    const result = await onGenerate({ persona, platform, purpose, tone });
    if (result) push("Content generated.", "success");
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2">
        <Sparkles className="h-4 w-4 text-accent" />
        <CardTitle>Generate content</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <p className="text-xs font-mono uppercase tracking-wider text-muted mb-2">
            Quick presets
          </p>
          <div className="flex flex-wrap gap-2">
            {TONE_PRESETS.map((preset) => (
              <button
                key={preset.value}
                onClick={() => setTone(preset.value)}
                className="rounded-full border border-border px-3 py-1 text-xs font-mono text-muted hover:text-accent hover:border-accent transition-colors"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        <PersonaSelector value={persona} onChange={setPersona} />
        <PlatformSelector value={platform} onChange={setPlatform} />
        <PurposeSelector value={purpose} onChange={setPurpose} />
        <ToneSelector value={tone} onChange={setTone} />

        <Button className="w-full" onClick={handleGenerate} disabled={generating}>
          {generating ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Generating…
            </>
          ) : (
            "Generate"
          )}
        </Button>

        {latestResult && (
          <div className="rounded-xl border border-border bg-surface-raised/60 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs font-mono text-accent">
                {titleCase(latestResult.purpose)} · {titleCase(latestResult.platform)} · for{" "}
                {titleCase(latestResult.persona)}
              </p>
              <div className="flex gap-2">
                <CopyButton text={latestResult.content} />
                <DownloadButton
                  text={latestResult.content}
                  filename={`${latestResult.platform}-${latestResult.purpose}-${latestResult.id}.txt`}
                />
              </div>
            </div>
            <p className="text-sm whitespace-pre-wrap leading-relaxed">{latestResult.content}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
