# PersonaStudio AI

**One Video. Infinite Content. Every Audience.**

PersonaStudio AI understands a video once — via either audio transcription or direct visual
analysis — extracting its meaning into a reusable **Content DNA**, and transforms that single
understanding into content for any audience, platform, purpose, and tone, without ever
re-analyzing the source video.

Built for the **AMD Developer Hackathon (Unicorn + Video Captioning Track)**.

* **GitHub Container Registry:** [PersonaStudio-AI Container](https://github.com/Ratul-byte/PersonaStudio-AI/pkgs/container/persona-studio)
* **Lablab.ai Submission:** [PersonaStudio AI Project Page](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii/trionda/persona-studio-ai)

---

## Table of contents

- [Core principle](#core-principle)
- [Understanding methods](#understanding-methods)
- [Architecture](#architecture)
- [Sequence diagram](#sequence-diagram)
- [Repository structure](#repository-structure)
- [Tech stack](#tech-stack)
- [Setup — AMD Developer Cloud JupyterLab](#setup--amd-developer-cloud-jupyterlab)
- [Environment variables](#environment-variables)
- [Supabase setup](#supabase-setup)
- [API documentation](#api-documentation)
- [Deployment](#deployment)
- [Testing](#testing)
- [Known limitations](#known-limitations)
- [Future-ready extension points](#future-ready-extension-points)

---

## Core principle

```
Video
  │
  ▼
Understand once (Whisper transcript OR Gemma 4 vision — pick one) + extract Content DNA
  │
  ▼
Save Content DNA (structured JSON, persisted in Supabase)
  │
  ▼
Reuse it for every future generation
```

Never analyze the same video twice. Every `/generate` call reuses the Content DNA produced
by the one `/analyze` call.

---

## Understanding methods

`POST /analyze` accepts an `understanding_method` field so the same video can be understood
in one of two ways — chosen once, per video, at analysis time:

| Method | `understanding_method` value | How it works | Requires |
|--------|-------------------------------|---------------|----------|
| **Whisper transcript** (default) | `whisper` | Extracts the audio track with `ffmpeg`, transcribes it via Groq's Whisper Large v3, then feeds the timestamped transcript to a Fireworks text LLM. | `GROQ_API_KEY`, `FIREWORKS_API_KEY` |
| **Gemma 4 vision** | `gemma_vision` | Samples 4 evenly-spaced frames from the video with `ffmpeg` and sends them directly to a vision-capable model via OpenRouter — **no audio transcription happens at all.** | `OPENROUTER_API_KEY` |

Both paths converge on the identical `ContentDNA` schema, so the Transformation Engine and
every frontend component are completely unaware of which method produced it. The choice is
surfaced in the Upload page UI (two selectable cards) and carried through to the Dashboard via
a `?method=` query param, shown there as a small badge.

If Content DNA already exists for a video, `understanding_method` is ignored — a video is only
ever analyzed once, by whichever method was used the first time. Passing an explicit
`raw_signal` to `/analyze` also overrides `understanding_method` entirely (skips both paths).

> **Cost note:** the vision path sends several base64-encoded JPEG frames per request, which
> is meaningfully more expensive per call than a text-only prompt. Worth checking your
> OpenRouter credit balance before relying on it for a live demo.

---

## Architecture

```
Frontend (Next.js)
       │
       ▼
   FastAPI (API layer)
       │
       ▼
Video Processing Service ───▶ Supabase Storage (uploaded video bytes)
       │
       ▼
Understanding Engine  (understanding_method picks ONE path per video)
   │
   ├─ "whisper" path
   │    ├─ ffmpeg: extract audio track from the stored video
   │    ├─ Groq (Whisper Large v3): transcribe audio → timestamped transcript
   │    └─ Fireworks LLM: transcript + metadata → structured Content DNA
   │
   └─ "gemma_vision" path
        ├─ ffmpeg: sample 4 evenly-spaced frames from the stored video
        └─ OpenRouter (Gemma 4, vision): frames + metadata → structured Content DNA
              (no transcription in this path)
       │
       ▼
   Content DNA (persisted as JSONB in Supabase Postgres)
       │
       ▼
Transformation Engine (Fireworks LLM)
       │
       ▼
   Output Formatter
       │
       ▼
Frontend (rendered content, copy/download/export)
```

Every provider sits behind an **abstract adapter interface** — `AIProvider`,
`StorageProvider`, `Database` — so swapping the LLM, storage backend, or database never
requires touching a route or a service's business logic, only a `.env` value.

## Sequence diagram

```
User        Frontend        FastAPI       DNAService                 TransformationService   Fireworks LLM
 │             │                │               │                             │                    │
 │ upload      │  POST /upload  │               │                             │                    │
 ├────────────▶│───────────────▶│──save(bytes)─▶ Supabase Storage             │                    │
 │             │◀───video_id────│               │                             │                    │
 │             │ POST /analyze  │               │                             │                    │
 ├────────────▶│───────────────▶│──analyze()───▶│                             │                    │
 │             │                │               │──ffmpeg: extract audio     │                    │
 │             │                │               │──Groq: transcribe audio    │                    │
 │             │                │               │──complete(prompt)───────────────────────────────▶│
 │             │                │               │◀────────────JSON Content DNA─────────────────────┤
 │             │                │◀──ContentDNA──┤                             │                    │
 │             │◀──ContentDNA───│               │                             │                    │
 │ pick persona/                │               │                             │                    │
 │ platform/tone│ POST /generate│               │                             │                    │
 ├────────────▶│───────────────▶│──generate(req,dna)─────────────────────────▶│                    │
 │             │                │               │                             │──complete(prompt)─▶│
 │             │                │               │                             │◀───generated text──┤
 │             │                │◀──────────────GenerationResult──────────────┤                    │
 │             │◀───result──────│               │                             │                    │
 │◀──rendered──│                │               │                             │                    │
```

> Diagram shows the `whisper` path. When `understanding_method=gemma_vision` is sent instead,
> the `DNAService` step swaps to: extract frames via `ffmpeg` → send frames + metadata directly
> to OpenRouter (Gemma 4) → same `ContentDNA` JSON comes back. Everything before and after that
> step (upload, generate, rendering) is identical regardless of which method was used.

---

## Repository structure

```
personastudio-ai/
├── backend/
│   └── app/
│       ├── main.py                     # FastAPI entrypoint
│       ├── api/
│       │   ├── deps.py                 # dependency-injection wiring
│       │   ├── router.py               # aggregates all routes
│       │   └── routes/                 # upload, video, analyze, generate, history
│       ├── core/                       # config.py, logger.py, exceptions.py
│       ├── models/                     # internal dataclasses (VideoRecord, GenerationRecord)
│       ├── schemas/                    # Pydantic API models (Content DNA, generation, video)
│       ├── services/
│       │   ├── video_service.py        # upload orchestration
│       │   ├── dna_service.py          # Understanding Engine: whisper (ffmpeg+Groq+Fireworks) OR gemma_vision (ffmpeg+OpenRouter)
│       │   ├── transformation_service.py  # Transformation Engine
│       │   ├── fireworks_service.py    # AIProvider adapter (Fireworks / mock)
│       │   ├── storage_service.py      # StorageProvider adapter (Supabase Storage)
│       │   └── database_services.py    # Database adapter (Supabase Postgres / JSON fallback)
│       ├── database/                   # Database interface + local JSON implementation
│       ├── prompts/                    # all prompts as .txt files (never hardcoded)
│       │   ├── understanding.txt       # text-based (whisper transcript) understanding prompt
│       │   └── understanding_vision.txt   # frames-based (gemma_vision) understanding prompt
│       └── workers/                    # Celery interface (scaffolded, not yet wired in)
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── app/                            # Next.js App Router pages
    │   ├── page.tsx                    # Home
    │   ├── upload/page.tsx
    │   ├── dashboard/[videoId]/page.tsx
    │   ├── history/page.tsx
    │   └── settings/page.tsx
    ├── components/                     # UploadCard (incl. understanding-method picker), TimelineViewer,
    │   │                                # DNAViewer, Persona/Platform/Purpose/ToneSelector,
    │   │                                # GeneratedContentPanel, HistoryPanel, ui/*
    ├── hooks/useVideoDashboard.ts
    ├── services/api.ts                 # single API client used by all pages
    └── types/index.ts
```

## Tech stack

| Layer          | Choice                                                                 |
|----------------|--------------------------------------------------------------------------|
| Frontend       | Next.js (App Router), React 18, TypeScript, TailwindCSS, Framer Motion, lucide-react |
| Backend        | FastAPI, Python 3.10+, Pydantic v2, pydantic-settings, Uvicorn        |
| LLM            | Fireworks AI — model set via `FIREWORKS_MODEL`, currently using serverless MiniMax M3 model |
| Transcription  | Groq (Whisper Large v3) — audio extracted from the uploaded video via `ffmpeg`. Used by the `whisper` understanding method. |
| Vision LLM     | OpenRouter (Gemma 4, vision-capable) — analyzes video frames sampled via `ffmpeg`, no transcription. Used by the `gemma_vision` understanding method. |
| Storage        | Supabase Storage (bucket configured via `SUPABASE_BUCKET`)             |
| Database       | Supabase Postgres (`videos` + `generations` tables) — JSON-file fallback available for local-only runs |
| Async/Queue    | Celery + Redis interface, scaffolded for future use — not currently invoked by any route |

> **Naming note:** the env var is called `GEMMA_MODEL` for historical reasons (it started as a
> Gemma-specific setting), but it now just holds whatever Fireworks model path the
> `AIProvider` adapter should call — it works with any Fireworks chat-completions model, not
> only Gemma. Nothing in the code assumes a specific model family.

---

## Setup — AMD Developer Cloud JupyterLab

Runs as a normal FastAPI + Next.js process inside a JupyterLab terminal — no notebook-specific
code required.

### 1. Backend

```bash
cd personastudio-ai/backend

python3 -m venv .venv
source .venv/bin/activate      # if `source` isn't found, try: . .venv/bin/activate

pip install -r requirements.txt --break-system-packages   # add this flag if pip refuses otherwise
```

**`ffmpeg` must also be installed as a system binary** (the `ffmpeg-python` package is just
Python bindings, not the encoder itself):

```bash
apt-get update && apt-get install -y ffmpeg
ffmpeg -version   # confirm it's on PATH
```

Configure environment — **the file must be named exactly `.env`** (pydantic-settings and
Next.js both only auto-load specific filenames; a custom name like `b.env` will be silently
ignored):

```bash
cp .env.example .env
# then edit .env — see "Environment variables" below
```

Run the API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Your JupyterLab host exposes this through its proxy, typically:
```
https://<your-jupyterlab-host>/proxy/8000/docs
```
(exact pattern depends on your provider — check for a "Ports" panel in the JupyterLab UI if unsure)

### 2. Frontend

```bash
cd personastudio-ai/frontend
npm install
cp .env.example .env.local
```
Set `NEXT_PUBLIC_API_BASE_URL` to your backend's proxied URL (browsers can't reach
`localhost` inside the JupyterLab container), e.g.:
```
NEXT_PUBLIC_API_BASE_URL=https://<your-jupyterlab-host>/proxy/8000/api/v1
```
Then:
```bash
npm run dev
```

If pages load unstyled or show 404s for `/_next/*` assets, the reverse-proxy subpath is
breaking Next's root-relative asset paths — set `basePath`/`assetPrefix` in
`frontend/next.config.js` to match your proxy prefix.

---

## Environment variables

`backend/.env` (all required unless noted):

```bash
# ---- App ----
APP_NAME=PersonaStudio AI
ENVIRONMENT=development
DEBUG=true
API_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3000        # add your JupyterLab proxy origin too if testing the frontend through it

# ---- AI Provider (Fireworks) ----
AI_PROVIDER=fireworks                     # fireworks | mock (mock needs no API key, useful for offline pipeline testing)
FIREWORKS_API_KEY=
FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
FIREWORKS_MODEL=accounts/fireworks/models/<your-chosen-model>   # must be a chat-capable model enabled on your Fireworks account — check with GET /v1/models

# ---- Transcription (Groq) ----
GROQ_API_KEY=                             # used by the "whisper" understanding method for Whisper Large v3 transcription

# ---- Vision understanding (OpenRouter Gemma 4) ----
OPENROUTER_API_KEY=                       # used by the "gemma_vision" understanding method
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_VISION_MODEL=google/gemma-4-31b-it   # verify availability at https://openrouter.ai/models

# ---- Storage ----
STORAGE_PROVIDER=supabase                 # currently the only supported path — see note below
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_BUCKET=PersonaStudio_AI

# ---- Database ----
DATABASE_PROVIDER=supabase                # json | supabase
JSON_DB_PATH=./storage/db.json            # only used when DATABASE_PROVIDER=json

# ---- Queue (future — not currently used) ----
REDIS_URL=redis://localhost:6379/0
```

> **Storage note:** `storage_service.py`'s factory currently always returns
> `SupabaseStorageProvider` regardless of `STORAGE_PROVIDER`'s value — local disk storage is
> temporarily disabled in code (see comments in that file). Supabase credentials are required
> to run the app at all right now, even for local dev.

`frontend/.env.local`:
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Supabase setup

Two tables are required — run this in the Supabase SQL editor:

```sql
create table videos (
  video_id         text primary key,
  filename         text not null,
  storage_path     text not null,
  content_type     text,
  size_bytes       bigint,
  duration_seconds double precision,
  status           text default 'uploaded',
  uploaded_at      timestamptz not null default now(),
  analyzed_at      timestamptz,
  content_dna      jsonb
);

create table generations (
  id          text primary key,
  video_id    text references videos(video_id) on delete cascade,
  persona     text not null,
  platform    text not null,
  purpose     text not null,
  tone        text not null,
  content     text not null,
  created_at  timestamptz not null default now()
);

create index on generations (video_id);
```

Also create a Storage bucket matching `SUPABASE_BUCKET` (default `PersonaStudio_AI`) in the
Supabase dashboard, and make sure your `SUPABASE_KEY` has permission to read/write it.

---

## API documentation

Interactive docs auto-generate at `/docs` (Swagger) and `/redoc`. Core endpoints:

| Method | Path                        | Description                                                        |
|--------|-----------------------------|----------------------------------------------------------------------|
| POST   | `/api/v1/upload`            | Upload a video file to Supabase Storage. Returns `video_id`. Does **not** analyze it. |
| GET    | `/api/v1/video/{video_id}`  | Return stored metadata for a video.                                 |
| POST   | `/api/v1/analyze`           | Run (or reuse) the Understanding Engine → extract Content DNA via `whisper` (transcribe) or `gemma_vision` (analyze frames directly). Accepts an optional `raw_signal` to skip both and supply a transcript/description manually. |
| POST   | `/api/v1/generate`          | Transform existing Content DNA into one piece of content.            |
| GET    | `/api/v1/history`           | List past generations, optionally filtered by `video_id`.            |
| GET    | `/health`                   | Health check.                                                        |

`POST /analyze` body — Whisper transcription (default):
```json
{
  "video_id": "vid_abc123",
  "understanding_method": "whisper"
}
```

`POST /analyze` body — Gemma 4 vision, no transcription:
```json
{
  "video_id": "vid_abc123",
  "understanding_method": "gemma_vision"
}
```

`POST /generate` body:
```json
{
  "video_id": "vid_abc123",
  "persona": "developer",
  "platform": "linkedin",
  "purpose": "caption",
  "tone": "formal"
}
```

---

## Deployment

### Backend → Render
1. Root directory: `backend/`
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   (or deploy the included `Dockerfile` directly — add `ffmpeg` to the image if you do, since the current `Dockerfile` doesn't install it yet)
4. Set all env vars from the table above; `CORS_ORIGINS` should be your Vercel domain.

### Frontend → Vercel
1. Root directory: `frontend/`
2. Framework preset: Next.js (auto-detected)
3. Env var: `NEXT_PUBLIC_API_BASE_URL=https://<your-render-service>.onrender.com/api/v1`

### Database & storage → Supabase
Already the primary backend for both — see [Supabase setup](#supabase-setup) above. No further
migration needed for deployment; same credentials, same tables.

---

## Testing

```bash
cd backend
pip install -r requirements.txt --break-system-packages
pytest tests/ -v
```
Tests run against `AI_PROVIDER=mock` and don't require live Fireworks/Groq/Supabase
credentials or network access.

---

## Known limitations

- **`ffmpeg` isn't in the Docker image yet** — add `apt-get install -y ffmpeg` to the
  `Dockerfile` before deploying, or both understanding methods will fail silently in
  production (audio extraction for `whisper`, frame extraction for `gemma_vision`).
- **Local storage path is currently unreachable** — `get_storage_provider()` always returns
  the Supabase provider; `STORAGE_PROVIDER=local` has no effect until that's re-enabled.
- **Transcripts aren't persisted as a queryable field** — `raw_signal` is set on the in-memory
  `VideoRecord` object during analysis but isn't part of the `VideoRecord`/`GenerationRecord`
  dataclasses or the Supabase `videos` table schema, so it isn't saved for later reuse. This
  only affects the `whisper` path — `gemma_vision` doesn't produce a transcript at all.
- **Model availability varies by account, for both providers** — always confirm `GEMMA_MODEL`
  against `GET https://api.fireworks.ai/inference/v1/models` and `OPENROUTER_VISION_MODEL`
  against `https://openrouter.ai/models` before assuming a given model path is reachable.
- **`gemma_vision` hasn't been live-tested end-to-end** — code is type/syntax-verified and the
  request/response shape follows OpenRouter's documented multimodal format, but an actual
  OpenRouter API call with real credentials hasn't been run yet. Test this before a live demo.
- **Vision path cost** — sends multiple base64-encoded frames per request, meaningfully pricier
  per call than the text-only `whisper` path. Check OpenRouter credit balance beforehand.
- **Celery/Redis are unused** — `REDIS_URL` and `workers/celery_app.py` are scaffolding only;
  `/analyze` and `/generate` both still run synchronously in-request.

---

## Future-ready extension points

Not implemented in the MVP, but the architecture doesn't require rework to add them:

- **Auth / organizations / projects / API keys / billing / team workspaces** — add a
  `User`/`Organization` model and a FastAPI auth dependency; every route already receives
  services via `Depends(...)`.
- **More LLM providers / understanding methods** — two exist today (Fireworks text via
  `whisper`, OpenRouter vision via `gemma_vision`); adding a third follows the same pattern —
  a new branch in `DNAService.analyze()` plus a dedicated prompt file.
- **Multilingual support** — pass a `language` field through `GenerationRequest` and prompt
  templates.
- **Async processing at scale** — implement the placeholder task in
  `workers/celery_app.py` and point `/analyze` at it once video volume justifies it.
- **Clip detection / SEO scoring / virality scoring / RAG over documents / chat with video** —
  new services that consume the existing `ContentDNA` object; no changes needed to the
  Understanding Engine's output contract.
