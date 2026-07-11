"use client";

import * as React from "react";
import { api, ApiError } from "@/services/api";
import type { ContentDNA, GenerationResult, Persona, Platform, Purpose, Tone, VideoMetadata } from "@/types";

interface UseVideoDashboardResult {
  video: VideoMetadata | null;
  dna: ContentDNA | null;
  loading: boolean;
  analyzing: boolean;
  error: string | null;
  generations: GenerationResult[];
  generate: (params: { persona: Persona; platform: Platform; purpose: Purpose; tone: Tone }) => Promise<GenerationResult | null>;
  generating: boolean;
}

/** Loads a video, ensures it has Content DNA (analyzing once if needed), and exposes generation actions. */
export function useVideoDashboard(videoId: string): UseVideoDashboardResult {
  const [video, setVideo] = React.useState<VideoMetadata | null>(null);
  const [dna, setDna] = React.useState<ContentDNA | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [analyzing, setAnalyzing] = React.useState(false);
  const [generating, setGenerating] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [generations, setGenerations] = React.useState<GenerationResult[]>([]);

  React.useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const meta = await api.getVideo(videoId);
        if (cancelled) return;
        setVideo(meta);

        if (meta.status === "analyzed") {
          // Content DNA already exists — pull it via analyze (idempotent reuse).
          setAnalyzing(true);
          const existingDna = await api.analyzeVideo(videoId);
          if (!cancelled) setDna(existingDna);
        } else {
          setAnalyzing(true);
          const newDna = await api.analyzeVideo(videoId);
          if (!cancelled) setDna(newDna);
        }

        const history = await api.getHistory(videoId);
        if (!cancelled) setGenerations(history);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Something went wrong loading this video.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
          setAnalyzing(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [videoId]);

  const generate = React.useCallback(
    async (params: { persona: Persona; platform: Platform; purpose: Purpose; tone: Tone }) => {
      setGenerating(true);
      try {
        const result = await api.generateContent({ video_id: videoId, ...params });
        setGenerations((prev) => [result, ...prev]);
        return result;
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Generation failed. Please try again.");
        return null;
      } finally {
        setGenerating(false);
      }
    },
    [videoId]
  );

  return { video, dna, loading, analyzing, error, generations, generate, generating };
}
