"use client";

import { PillSelect } from "@/components/ui/pill-select";
import type { Purpose } from "@/types";

const PURPOSES: { value: Purpose; label: string }[] = [
  { value: "caption", label: "Caption" },
  { value: "summary", label: "Summary" },
  { value: "blog", label: "Blog" },
  { value: "article", label: "Article" },
  { value: "meeting_notes", label: "Meeting Notes" },
  { value: "documentation", label: "Documentation" },
  { value: "research_draft", label: "Research Draft" },
  { value: "press_release", label: "Press Release" },
];

export function PurposeSelector({ value, onChange }: { value: Purpose; onChange: (v: Purpose) => void }) {
  return (
    <PillSelect
      label="Purpose"
      options={PURPOSES}
      value={value}
      onChange={(v) => onChange(v as Purpose)}
    />
  );
}
