"use client";

import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DnaBranchHero } from "@/components/DnaBranchHero";
import { Card, CardContent } from "@/components/ui/card";

const steps = [
  {
    step: "Understand",
    title: "Analyze the video once",
    body: "PersonaStudio watches a video a single time and extracts a structured Content DNA — summary, timeline, tone, entities, topics, and core message.",
  },
  {
    step: "Transform",
    title: "Reuse that understanding",
    body: "Every generation reuses the same Content DNA. The video is never re-analyzed — Gemma transforms meaning, not pixels, on every request.",
  },
  {
    step: "Publish",
    title: "Ship content for every audience",
    body: "Pick a persona, platform, purpose, and tone. Get a LinkedIn post, a sarcastic caption, a press release, or a research abstract — instantly.",
  },
];

export default function HomePage() {
  return (
    <div className="overflow-hidden relative">
      {/* Background ambient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary/10 blur-[120px] rounded-full pointer-events-none -z-10" />

      <section className="mx-auto max-w-6xl px-6 pt-16 pb-20 grid md:grid-cols-2 gap-12 items-center">
        <div>
          {/* Staggered text entrances */}
          <div className="animate-in fade-in slide-in-from-bottom-6 duration-700 ease-out fill-mode-both">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1 text-xs font-mono text-accent mb-6 hover:border-accent/50 transition-colors">
              <Sparkles className="h-3 w-3 animate-pulse" /> AMD Developer Hackathon — Unicorn Track
            </span>
          </div>
          
          <div className="animate-in fade-in slide-in-from-bottom-6 duration-700 delay-150 ease-out fill-mode-both">
            <h1 className="font-display text-4xl md:text-5xl font-semibold tracking-tight leading-[1.1] mb-5">
              One video.
              <br />
              Infinite content.
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Every audience.</span>
            </h1>
          </div>
          
          <div className="animate-in fade-in slide-in-from-bottom-6 duration-700 delay-300 ease-out fill-mode-both">
            <p className="text-muted text-base md:text-lg max-w-md mb-8 leading-relaxed">
              PersonaStudio AI understands a video once, extracts its meaning as reusable Content
              DNA, and transforms that understanding into content for any audience, platform, or
              purpose — without ever re-analyzing the source.
            </p>
          </div>

          <div className="flex gap-3 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-500 ease-out fill-mode-both">
            <Link href="/upload">
              <Button size="lg" className="group transition-all duration-300 hover:scale-105 hover:shadow-[0_0_20px_rgba(124,92,252,0.3)]">
                Upload a video <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/history">
              <Button size="lg" variant="secondary" className="transition-all duration-300 hover:scale-105">
                View history
              </Button>
            </Link>
          </div>
        </div>
        
        <div className="animate-in fade-in zoom-in-95 duration-1000 delay-300 fill-mode-both">
          <DnaBranchHero />
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="grid md:grid-cols-3 gap-5">
          {steps.map((s, index) => (
            <div 
              key={s.step} 
              className="animate-in fade-in slide-in-from-bottom-8 duration-700 fill-mode-both"
              style={{ animationDelay: `${700 + (index * 150)}ms` }}
            >
              <Card className="h-full transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl hover:border-primary/40 group">
                <CardContent>
                  <p className="font-mono text-xs uppercase tracking-wider text-accent mb-3 group-hover:text-primary transition-colors duration-300">
                    {s.step}
                  </p>
                  <h3 className="font-display text-lg font-semibold mb-2">{s.title}</h3>
                  <p className="text-sm text-muted leading-relaxed group-hover:text-foreground/80 transition-colors duration-300">{s.body}</p>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}