"use client";

import { PillSelect } from "@/components/ui/pill-select";
import type { Platform } from "@/types";

const PLATFORMS: { value: Platform; label: string }[] = [
  { value: "linkedin", label: "LinkedIn" },
  { value: "instagram", label: "Instagram" },
  { value: "x", label: "X / Twitter" },
  { value: "youtube", label: "YouTube" },
  { value: "blog", label: "Blog" },
  { value: "newsletter", label: "Newsletter" },
];

export function PlatformSelector({ value, onChange }: { value: Platform; onChange: (v: Platform) => void }) {
  return (
    <PillSelect
      label="Platform"
      options={PLATFORMS}
      value={value}
      onChange={(v) => onChange(v as Platform)}
    />
  );
}
