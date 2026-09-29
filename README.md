# OptiCode — Backend A

> Core application orchestration layer for the AI-powered coding workspace.

## Overview

Backend A is the **central orchestrator** of the OptiCode system. It receives
requests from the frontend, authenticates users, manages conversations, delegates
code analysis to Backend B, sends AI requests through a provider abstraction,
persists results, and returns clean responses.

```
USER → FRONTEND → BACKEND A → Backend B (code analysis)
                             → AI Provider (response generation)
                             → Supabase (persistence / auth)
                             → FRONTEND → USER
```

## Current Implementation Status

| Component | Status |
|---|---|
| FastAPI application factory | ✅ Implemented |
| Health endpoint (`GET /health`) | ✅ Implemented |
| Configuration (pydantic-settings) | ✅ Implemented |
| Structured error handling | ✅ Implemented |
| Request ID middleware | ✅ Implemented |
| CORS middleware | ✅ Implemented |
| Structured logging | ✅ Implemented |
| Dependency injection foundation | ✅ Implemented |
| Router structure (all routes registered) | ✅ Implemented |
| Test infrastructure (80 tests passing) | ✅ Implemented |
| Supabase client integration | ✅ Implemented (Phase 2) |
| Database schema & SQL migration | ✅ Implemented (Phase 2) |
| Row Level Security (RLS) policies | ✅ Implemented (Phase 2) |
| Repositories (`user`, `conversation`, `message`) | ✅ Implemented (Phase 2) |
| Services (`conversation`, `message` + ownership) | ✅ Implemented (Phase 2) |
| Conversation routes (`/conversations/*`) | ✅ Implemented (Phase 2) |
| Message routes (`/conversations/*/messages`) | ✅ Implemented (Phase 2) |
| Auth routes (`/auth/*`) | 🔲 Stub (501 — Phase 3) |
| Code operation routes (`/code/*`) | 🔲 Stub (501 — Phase 5+) |
| Full Auth JWT token issuance | 🔲 Not started (Phase 3) |
| Backend B integration | 🔲 Not started (Phase 5) |
| AI provider integration | 🔲 Not started (Phase 6) |
| Orchestration pipeline | 🔲 Not started (Phase 7) |

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | Supabase (PostgreSQL) — schema & client implemented |
| Auth | Supabase Auth (JWT) — identity parsing implemented; full auth in Phase 3 |
| AI | OpenAI / Gemini (provider abstraction) — *not yet integrated* |
| Code Analysis | Backend B (external service) — *not yet integrated* |

## Architecture

```
app/
├── api/              # FastAPI routes and dependencies
│   ├── deps.py       # Dependency injection (get_settings, get_supabase, get_current_user_id)
│   ├── router.py     # Aggregates all route modules
│   └── routes/       # Route handlers (/health, /conversations, /messages, etc.)
├── schemas/          # Pydantic request/response models (conversations, messages, common)
├── services/         # Application logic and ownership boundaries (ConversationService, MessageService)
├── repositories/     # Data-access layer (UserRepository, ConversationRepository, MessageRepository)
├── integrations/     # External service clients
│   ├── supabase_client.py # Managed Supabase client
│   ├── backend_b/    # Backend B interface + client (future)
│   └── ai_provider/  # AI provider abstraction + implementations (future)
├── core/             # Errors, error handlers, logging, context, security
└── middleware/        # CORS, request-ID injection
supabase/
└── migrations/       # SQL schema migrations (20260929000000_initial_schema.sql)
```

## Database Schema & Ownership Model

### Schema Overview

- **`public.users`**:
  - `id` (UUID, Primary Key)
  - `created_at` (TIMESTAMPTZ), `updated_at` (TIMESTAMPTZ)
- **`public.conversations`**:
  - `id` (UUID, Primary Key, default `gen_random_uuid()`)
  - `user_id` (UUID, Foreign Key → `users.id` ON DELETE CASCADE)
  - `title` (TEXT, NOT NULL)
  - `created_at` (TIMESTAMPTZ), `updated_at` (TIMESTAMPTZ)
  - Indexes: `idx_conversations_user_id`, `idx_conversations_updated_at`
- **`public.messages`**:
  - `id` (UUID, Primary Key, default `gen_random_uuid()`)
  - `conversation_id` (UUID, Foreign Key → `conversations.id` ON DELETE CASCADE)
  - `role` (TEXT, CHECK `role IN ('user', 'assistant', 'system')`)
  - `content` (TEXT, NOT NULL)
  - `metadata` (JSONB, NOT NULL, default `'{}'::jsonb`)
  - `created_at` (TIMESTAMPTZ)
  - Indexes: `idx_messages_conversation_id`, `idx_messages_chronological`

### Row Level Security (RLS) & Ownership

Defense-in-depth is enforced at two distinct layers:
1. **Application Layer (`services/`)**:
   - `ConversationService` validates that `conversation.user_id == authenticated_user_id`. Non-owners receive `403 AuthorizationError`.
   - `MessageService` validates that the requesting user owns the parent conversation before creating or listing messages.
2. **Database Layer (RLS)**:
   - RLS is enabled on all tables.
   - `conversations` policy: `auth.uid() = user_id`.
   - `messages` policy: `EXISTS (SELECT 1 FROM conversations WHERE conversations.id = messages.conversation_id AND conversations.user_id = auth.uid())`.

## Quick Start

### Prerequisites

- **Python 3.12** (3.12.x recommended)

### Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Install dependencies (including dev tools)
pip install -e ".[dev]"

# 3. (Optional) Copy and configure environment
cp .env.example .env
# Edit .env to supply SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY if connecting to Supabase
```

### Applying Migrations

#### Option A: Supabase CLI (Local Development)
```bash
supabase db reset
# or
supabase migration up
```

#### Option B: Supabase Dashboard (Cloud Project)
1. Open your Supabase Dashboard SQL Editor.
2. Copy and execute the contents of [`supabase/migrations/20260929000000_initial_schema.sql`](supabase/migrations/20260929000000_initial_schema.sql).

### Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

The server starts at `http://localhost:8000`.

### Verify

```bash
curl http://localhost:8000/health
# → {"status":"ok","service":"opticode-backend-a"}
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```

> **Note on Tests**: All tests run completely offline without requiring credentials or network access to a real Supabase database. Repositories and services are thoroughly tested via test doubles and dependency injection overrides.

## Endpoints

| Method | Path | Status | Description |
|---|---|---|---|
| `GET` | `/health` | ✅ Live | Service liveness probe |
| `GET` | `/docs` | ✅ Live | Swagger UI |
| `GET` | `/redoc` | ✅ Live | ReDoc |
| `POST` | `/conversations` | ✅ Live | Create new conversation |
| `GET` | `/conversations` | ✅ Live | List user conversations |
| `GET` | `/conversations/{id}` | ✅ Live | Get single conversation |
| `PATCH` | `/conversations/{id}` | ✅ Live | Update conversation title |
| `DELETE` | `/conversations/{id}` | ✅ Live | Delete conversation |
| `GET` | `/conversations/{id}/messages` | ✅ Live | List conversation messages |
| `POST` | `/conversations/{id}/messages` | ✅ Live | Post message to conversation |
| `POST` | `/auth/signup` | 501 | Register user (Phase 3) |
| `POST` | `/auth/login` | 501 | Sign in (Phase 3) |
| `POST` | `/auth/logout` | 501 | Sign out (Phase 3) |
| `POST` | `/auth/refresh` | 501 | Refresh token (Phase 3) |
| `POST` | `/code/optimize` | 501 | Optimize code (Phase 5+) |
| `POST` | `/code/fix` | 501 | Fix code (Phase 5+) |
| `POST` | `/code/explain` | 501 | Explain code (Phase 5+) |

## License

MIT
