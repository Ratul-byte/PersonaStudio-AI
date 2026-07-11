"use client";

import { PillSelect } from "@/components/ui/pill-select";
import type { Persona } from "@/types";

const PERSONAS: { value: Persona; label: string }[] = [
  { value: "developer", label: "Developer" },
  { value: "researcher", label: "Researcher" },
  { value: "teacher", label: "Teacher" },
  { value: "student", label: "Student" },
  { value: "investor", label: "Investor" },
  { value: "journalist", label: "Journalist" },
  { value: "marketing", label: "Marketing" },
  { value: "recruiter", label: "Recruiter" },
  { value: "ceo", label: "CEO" },
];

export function PersonaSelector({ value, onChange }: { value: Persona; onChange: (v: Persona) => void }) {
  return (
    <PillSelect
      label="Audience"
      options={PERSONAS}
      value={value}
      onChange={(v) => onChange(v as Persona)}
    />
  );
}
