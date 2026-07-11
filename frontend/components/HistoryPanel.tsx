import { useState } from "react";
import { History as HistoryIcon, Eye, X } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/CopyButton";
import type { GenerationResult } from "@/types";
import { formatTimestamp, titleCase } from "@/lib/utils";

export function HistoryPanel({ generations }: { generations: GenerationResult[] }) {
  // State to manage the currently selected text for the popup modal
  const [selectedText, setSelectedText] = useState<string | null>(null);

  return (
    <>
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
                  <div className="flex items-center gap-1.5">
                    {/* View Button */}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 px-2 text-xs gap-1 text-muted-foreground hover:text-foreground"
                      onClick={() => setSelectedText(g.content)}
                    >
                      <Eye className="h-3.5 w-3.5" />
                      View
                    </Button>
                    <CopyButton text={g.content} />
                  </div>
                </div>
                <p className="text-sm text-muted line-clamp-3">{g.content}</p>
                <p className="text-[11px] text-muted mt-2 font-mono">{formatTimestamp(g.created_at)}</p>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Pop-up Modal / Dialog Layer */}
      {selectedText !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div 
            className="bg-card border border-border rounded-xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <h3 className="text-sm font-semibold text-foreground">Generated Content View</h3>
              <div className="flex items-center gap-2">
                <CopyButton text={selectedText} />
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 text-muted-foreground hover:text-foreground"
                  onClick={() => setSelectedText(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-4 overflow-y-auto font-sans text-sm text-foreground space-y-2 whitespace-pre-wrap selection:bg-accent/30">
              {selectedText}
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end border-t border-border px-4 py-3 bg-muted/20">
              <Button variant="outline" size="sm" onClick={() => setSelectedText(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}