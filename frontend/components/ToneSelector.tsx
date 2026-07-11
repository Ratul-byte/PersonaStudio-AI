"use client";

import { PillSelect } from "@/components/ui/pill-select";
import type { Tone } from "@/types";

const TONES: { value: Tone; label: string }[] = [
  { value: "formal", label: "Formal" },
  { value: "sarcastic", label: "Sarcastic" },
  { value: "humorous_tech", label: "Humorous (Tech)" },
  { value: "humorous_non_tech", label: "Humorous (Non-Tech)" },
  { value: "professional", label: "Professional" },
  { value: "casual", label: "Casual" },
  { value: "enthusiastic", label: "Enthusiastic" },
];

// Track 2 compatibility: one-click presets that simply populate the tone control.
export const TONE_PRESETS: { value: Tone; label: string }[] = [
  { value: "formal", label: "Formal" },
  { value: "sarcastic", label: "Sarcastic" },
  { value: "humorous_tech", label: "Humorous Tech" },
  { value: "humorous_non_tech", label: "Humorous Non-Tech" },
];

export function ToneSelector({ value, onChange }: { value: Tone; onChange: (v: Tone) => void }) {
  return (
    <PillSelect
      label="Tone"
      options={TONES}
      value={value}
      onChange={(v) => onChange(v as Tone)}
    />
  );
}
