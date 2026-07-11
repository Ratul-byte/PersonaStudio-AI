import type { ContentDNA, GenerationResult, Persona, Platform, Purpose, Tone, VideoMetadata } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let message = response.statusText;
    try {
      const body = await response.json();
      message = body.message || message;
    } catch {
      // ignore body parse errors
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

export const api = {
  /** Upload a video file. Returns immediately; the video is not analyzed yet. */
  uploadVideo: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ video_id: string; filename: string; status: string; uploaded_at: string }>(
      "/upload",
      { method: "POST", body: formData }
    );
  },

  /** Fetch metadata for a previously uploaded video. */
  getVideo: (videoId: string) => request<VideoMetadata>(`/video/${videoId}`),

  /** Run (or reuse) the Understanding Engine to produce Content DNA. */
  analyzeVideo: (videoId: string, rawSignal?: string) =>
    request<ContentDNA>("/analyze", {
      method: "POST",
      body: JSON.stringify({ video_id: videoId, raw_signal: rawSignal }),
    }),

  /** Transform existing Content DNA into one piece of audience/platform-specific content. */
  generateContent: (params: {
    video_id: string;
    persona: Persona;
    platform: Platform;
    purpose: Purpose;
    tone: Tone;
  }) =>
    request<GenerationResult>("/generate", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  /** List past generations, optionally scoped to a single video. */
  getHistory: (videoId?: string) =>
    request<GenerationResult[]>(`/history${videoId ? `?video_id=${videoId}` : ""}`),
};

export { ApiError };
