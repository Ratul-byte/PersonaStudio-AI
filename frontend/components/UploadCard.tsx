"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileVideo, Loader2, AudioLines, Eye } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { api, ApiError } from "@/services/api";
import { cn } from "@/lib/utils";
import type { UnderstandingMethod } from "@/types";

const METHODS: { value: UnderstandingMethod; label: string; description: string; icon: React.ReactNode }[] = [
  {
    value: "whisper",
    label: "Transcribe audio (Whisper)",
    description: "Extracts and transcribes the audio track, then analyzes the transcript.",
    icon: <AudioLines className="h-4 w-4" />,
  },
  {
    value: "gemma_vision",
    label: "Analyze frames directly (Gemma 4 vision)",
    description: "Samples frames from the video and analyzes them visually — no audio transcription.",
    icon: <Eye className="h-4 w-4" />,
  },
];

export function UploadCard() {
  const [dragging, setDragging] = React.useState(false);
  const [file, setFile] = React.useState<File | null>(null);
  const [uploading, setUploading] = React.useState(false);
  const [method, setMethod] = React.useState<UnderstandingMethod>("whisper");
  const inputRef = React.useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { push } = useToast();

  const handleFiles = (files: FileList | null) => {
    if (files && files[0]) setFile(files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const result = await api.uploadVideo(file);
      push(`"${result.filename}" uploaded. Starting analysis…`, "success");
      router.push(`/dashboard/${result.video_id}?method=${method}`);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Upload failed. Please try again.";
      push(message, "error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            handleFiles(e.dataTransfer.files);
          }}
          onClick={() => inputRef.current?.click()}
          className={cn(
            "flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed px-6 py-16 text-center cursor-pointer transition-colors",
            dragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept="video/mp4,video/quicktime,video/x-matroska,video/webm"
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
          {file ? (
            <>
              <FileVideo className="h-8 w-8 text-accent" />
              <p className="font-mono text-sm">{file.name}</p>
              <p className="text-xs text-muted">{(file.size / (1024 * 1024)).toFixed(1)} MB</p>
            </>
          ) : (
            <>
              <UploadCloud className="h-8 w-8 text-muted" />
              <p className="text-sm">
                Drag & drop a video here, or <span className="text-primary">browse</span>
              </p>
              <p className="text-xs text-muted">MP4, MOV, MKV, or WebM</p>
            </>
          )}
        </div>

        <div className="mt-6">
          <p className="text-xs font-mono uppercase tracking-wider text-muted mb-2">
            How should we understand this video?
          </p>
          <div className="space-y-2">
            {METHODS.map((m) => {
              const active = method === m.value;
              return (
                <button
                  key={m.value}
                  type="button"
                  onClick={() => setMethod(m.value)}
                  className={cn(
                    "w-full flex items-start gap-3 rounded-xl border px-3 py-2.5 text-left transition-colors",
                    active
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50"
                  )}
                >
                  <span className={cn("mt-0.5", active ? "text-primary" : "text-muted")}>
                    {m.icon}
                  </span>
                  <span>
                    <span className="block text-sm">{m.label}</span>
                    <span className="block text-xs text-muted mt-0.5">{m.description}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <Button className="w-full mt-5" onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Uploading…
            </>
          ) : (
            "Upload & continue"
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
