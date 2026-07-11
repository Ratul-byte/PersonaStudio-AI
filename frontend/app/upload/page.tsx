import { UploadCard } from "@/components/UploadCard";

export default function UploadPage() {
  return (
    <div className="mx-auto max-w-xl px-6 py-16">
      <h1 className="font-display text-2xl font-semibold mb-2">Upload a video</h1>
      <p className="text-sm text-muted mb-8">
        We'll analyze it once, extract its Content DNA, and take you straight to the dashboard.
      </p>
      <UploadCard />
    </div>
  );
}
