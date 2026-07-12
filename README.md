# PersonaStudio AI

**One Video. Infinite Content. Every Audience.**

PersonaStudio AI understands a video once — transcribing it, extracting its meaning into a
reusable **Content DNA** — and transforms that single understanding into content for any
audience, platform, purpose, and tone, without ever re-analyzing the source video.

Built for the **AMD Developer Hackathon (Unicorn Track)**.

---

## Table of contents

- [Core principle](#core-principle)
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
Transcribe once (Groq Whisper) + extract understanding once (Fireworks LLM)
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
Understanding Engine
   ├─ ffmpeg: extract audio track from the stored video
   ├─ Groq (Whisper Large v3): transcribe audio → timestamped transcript
   └─ Fireworks LLM: transcript + metadata → structured Content DNA
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
│       │   ├── dna_service.py          # Understanding Engine: ffmpeg + Groq + Fireworks
│       │   ├── transformation_service.py  # Transformation Engine
│       │   ├── fireworks_service.py    # AIProvider adapter (Fireworks / mock)
│       │   ├── storage_service.py      # StorageProvider adapter (Supabase Storage)
│       │   └── database_services.py    # Database adapter (Supabase Postgres / JSON fallback)
│       ├── database/                   # Database interface + local JSON implementation
│       ├── prompts/                    # all prompts as .txt files (never hardcoded)
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
    ├── components/                     # UploadCard, TimelineViewer, DNAViewer,
    │   │                                # Persona/Platform/Purpose/ToneSelector,
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
| LLM            | Fireworks AI — model set via `GEMMA_MODEL`, currently pointed at a non-Gemma chat model (see note below) |
| Transcription  | Groq (Whisper Large v3) — audio extracted from the uploaded video via `ffmpeg` |
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
GEMMA_MODEL=accounts/fireworks/models/<your-chosen-model>   # must be a chat-capable model enabled on your Fireworks account — check with GET /v1/models

# ---- Transcription (Groq) ----
GROQ_API_KEY=                             # required whenever STORAGE_PROVIDER=supabase; used for Whisper Large v3 transcription

# ---- Storage ----
STORAGE_PROVIDER=supabase                 # currently the only supported path — see note below
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_BUCKET=

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
| POST   | `/api/v1/analyze`           | Run (or reuse) the Understanding Engine → transcribe + extract Content DNA. Accepts an optional `raw_signal` to skip auto-transcription. |
| POST   | `/api/v1/generate`          | Transform existing Content DNA into one piece of content.            |
| GET    | `/api/v1/history`           | List past generations, optionally filtered by `video_id`.            |
| GET    | `/health`                   | Health check.                                                        |

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
  `Dockerfile` before deploying, or audio transcription will fail silently in production.
- **Local storage path is currently unreachable** — `get_storage_provider()` always returns
  the Supabase provider; `STORAGE_PROVIDER=local` has no effect until that's re-enabled.
- **Transcripts aren't persisted as a queryable field** — `raw_signal` is set on the in-memory
  `VideoRecord` object during analysis but isn't part of the `VideoRecord`/`GenerationRecord`
  dataclasses or the Supabase `videos` table schema, so it isn't saved for later reuse.
- **Model availability varies by Fireworks account** — always confirm your `GEMMA_MODEL`
  value against `GET https://api.fireworks.ai/inference/v1/models` for your account before
  assuming a given model path is deployed and reachable.
- **Celery/Redis are unused** — `REDIS_URL` and `workers/celery_app.py` are scaffolding only;
  `/analyze` and `/generate` both still run synchronously in-request.

---

## Future-ready extension points

Not implemented in the MVP, but the architecture doesn't require rework to add them:

- **Auth / organizations / projects / API keys / billing / team workspaces** — add a
  `User`/`Organization` model and a FastAPI auth dependency; every route already receives
  services via `Depends(...)`.
- **Multiple LLM providers** — implement a new `AIProvider` subclass in
  `fireworks_service.py` and add a branch to `get_ai_provider()`.
- **Multilingual support** — pass a `language` field through `GenerationRequest` and prompt
  templates.
- **Async processing at scale** — implement the placeholder task in
  `workers/celery_app.py` and point `/analyze` at it once video volume justifies it.
- **Clip detection / SEO scoring / virality scoring / RAG over documents / chat with video** —
  new services that consume the existing `ContentDNA` object; no changes needed to the
  Understanding Engine's output contract.
