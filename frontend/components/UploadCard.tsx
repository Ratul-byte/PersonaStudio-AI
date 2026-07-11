"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileVideo, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { api, ApiError } from "@/services/api";
import { cn } from "@/lib/utils";

export function UploadCard() {
  const [dragging, setDragging] = React.useState(false);
  const [file, setFile] = React.useState<File | null>(null);
  const [uploading, setUploading] = React.useState(false);
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
      router.push(`/dashboard/${result.video_id}`);
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
