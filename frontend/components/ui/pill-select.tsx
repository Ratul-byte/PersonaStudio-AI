"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface PillOption {
  value: string;
  label: string;
  icon?: React.ReactNode;
}

interface PillSelectProps {
  label: string;
  options: PillOption[];
  value: string;
  onChange: (value: string) => void;
}

/** A row of selectable pills — the shared control behind every selector panel. */
export function PillSelect({ label, options, value, onChange }: PillSelectProps) {
  return (
    <div>
      <p className="text-xs font-mono uppercase tracking-wider text-muted mb-2">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const active = opt.value === value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange(opt.value)}
              className={cn(
                "flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-colors",
                active
                  ? "border-primary bg-primary/15 text-foreground"
                  : "border-border bg-surface-raised/50 text-muted hover:text-foreground hover:border-primary/50"
              )}
            >
              {opt.icon}
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
