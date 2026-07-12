export type UnderstandingMethod = "whisper" | "gemma_vision";

export type Persona =
  | "developer"
  | "researcher"
  | "teacher"
  | "student"
  | "investor"
  | "journalist"
  | "marketing"
  | "recruiter"
  | "ceo";

export type Platform = "linkedin" | "instagram" | "x" | "youtube" | "blog" | "newsletter";

export type Purpose =
  | "caption"
  | "summary"
  | "blog"
  | "article"
  | "meeting_notes"
  | "documentation"
  | "research_draft"
  | "press_release";

export type Tone =
  | "formal"
  | "sarcastic"
  | "humorous_tech"
  | "humorous_non_tech"
  | "professional"
  | "casual"
  | "enthusiastic";

export interface VideoMetadata {
  video_id: string;
  filename: string;
  duration_seconds: number | null;
  size_bytes: number | null;
  content_type: string | null;
  storage_path: string;
  status: "uploaded" | "analyzing" | "analyzed" | "failed";
  uploaded_at: string;
  analyzed_at: string | null;
}

export interface TimelineEvent {
  timestamp_seconds: number;
  label: string;
}

export interface ContentDNA {
  video_id: string;
  title: string;
  summary: string;
  core_message: string;
  tone: string;
  sentiment: string;
  timeline: TimelineEvent[];
  key_events: string[];
  detected_objects: string[];
  people: string[];
  activities: string[];
  important_timestamps: TimelineEvent[];
  keywords: string[];
  entities: string[];
  topics: string[];
  context: string;
}

export interface GenerationResult {
  id: string;
  video_id: string;
  persona: Persona;
  platform: Platform;
  purpose: Purpose;
  tone: Tone;
  content: string;
  created_at: string;
}
