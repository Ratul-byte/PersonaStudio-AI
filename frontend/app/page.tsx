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
    <div>
      <section className="mx-auto max-w-6xl px-6 pt-16 pb-20 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1 text-xs font-mono text-accent mb-6">
            <Sparkles className="h-3 w-3" /> AMD Developer Hackathon — Unicorn Track
          </span>
          <h1 className="font-display text-4xl md:text-5xl font-semibold tracking-tight leading-[1.1] mb-5">
            One video.
            <br />
            Infinite content.
            <br />
            <span className="text-primary">Every audience.</span>
          </h1>
          <p className="text-muted text-base md:text-lg max-w-md mb-8">
            PersonaStudio AI understands a video once, extracts its meaning as reusable Content
            DNA, and transforms that understanding into content for any audience, platform, or
            purpose — without ever re-analyzing the source.
          </p>
          <div className="flex gap-3">
            <Link href="/upload">
              <Button size="lg">
                Upload a video <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/history">
              <Button size="lg" variant="secondary">
                View history
              </Button>
            </Link>
          </div>
        </div>
        <DnaBranchHero />
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="grid md:grid-cols-3 gap-5">
          {steps.map((s) => (
            <Card key={s.step}>
              <CardContent>
                <p className="font-mono text-xs uppercase tracking-wider text-accent mb-3">
                  {s.step}
                </p>
                <h3 className="font-display text-lg font-semibold mb-2">{s.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{s.body}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
