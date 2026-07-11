"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sun, Moon } from "lucide-react";

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
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Check local storage on load, default to dark if nothing is saved
    const savedTheme = localStorage.getItem("ps_theme") as "light" | "dark" | null;
    
    if (savedTheme === "light") {
      setTheme("light");
      document.documentElement.classList.remove("dark");
    } else {
      setTheme("dark");
      document.documentElement.classList.add("dark");
      localStorage.setItem("ps_theme", "dark");
    }
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    localStorage.setItem("ps_theme", nextTheme);

    if (nextTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  // Prevent hydration errors by not rendering the UI until the theme is loaded
  if (!mounted) return null;

  return (
    <div className="mx-auto max-w-2xl px-6 py-16 space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold mb-2">Settings</h1>
        <p className="text-sm text-muted">Environment and account configuration.</p>
      </div>

      {/* Preferences Section */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-foreground">Interface Theme</p>
            <p className="text-xs text-muted">
              Switch between clear visibility and low-light optimization.
            </p>
          </div>
          <Button
            variant="outline"
            onClick={toggleTheme}
            className="gap-2 min-w-[120px] justify-center"
          >
            {theme === "dark" ? (
              <>
                <Moon className="h-4 w-4 text-accent" />
                Dark Mode
              </>
            ) : (
              <>
                <Sun className="h-4 w-4 text-yellow-500" />
                Light Mode
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Preserved coming soon layout */}
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