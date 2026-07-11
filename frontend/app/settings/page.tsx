import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const upcoming = [
  "Authentication",
  "Organizations",
  "Projects",
  "API keys",
  "Billing",
  "Team workspaces",
  "Multilingual support",
  "Analytics",
];

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-16 space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold mb-2">Settings</h1>
        <p className="text-sm text-muted">Environment and account configuration.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Connection</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted mb-1">API base URL</p>
          <p className="font-mono text-sm text-accent">
            {process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"}
          </p>
          <p className="text-xs text-muted mt-2">
            Set via <code className="font-mono">NEXT_PUBLIC_API_BASE_URL</code> — no code changes
            needed between local dev and production.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Coming soon</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted mb-3">
            The architecture already keeps interfaces ready for these — no rework needed to add
            them later.
          </p>
          <div className="flex flex-wrap gap-2">
            {upcoming.map((item) => (
              <Badge key={item}>{item}</Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
