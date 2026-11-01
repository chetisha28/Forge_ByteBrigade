# 04 — Technology Stack and Rationale

## Recommended stack

### Frontend
- React + TypeScript + Vite.
- Tailwind CSS.
- Use shadcn/ui selectively for accessible primitives; do not let the default component look dictate the entire product.
- React Router for routing.
- TanStack Query for server state if API complexity warrants it.
- React Hook Form + Zod for forms and client-side validation.
- Lucide icons, used consistently.

### Backend
- Python 3.12+ (choose a version supported by all pinned dependencies).
- FastAPI.
- Pydantic v2 for request/response validation and settings.
- SQLAlchemy 2.x for database access.
- Alembic for schema migrations.
- Supabase Python client only where it materially simplifies Auth/Storage; use SQLAlchemy for core relational queries.

### Data and infrastructure
- Supabase-managed PostgreSQL.
- pgvector extension for embeddings.
- Supabase Auth for identity.
- Supabase Storage for private user documents.
- Render for FastAPI deployment; Vercel for frontend deployment.

### AI
- Official Google Gen AI Python SDK (`google-genai`), not deprecated legacy SDKs.
- Gemini generative model selected through environment configuration; use a stable generally available model available to the project's API key.
- Gemini Embedding 2 (`gemini-embedding-2`) for embeddings if available to the project account. Set a fixed output dimensionality, such as 768, and make the DB vector dimension match.
- Keep model IDs configurable; do not scatter model names across source files.
- Structured output / Pydantic response schemas for extraction and classification where supported.
- RAG retrieval implemented directly with SQLAlchemy/pgvector initially. Avoid adding LangChain unless a real requirement emerges.

### Document handling
- PyMuPDF for text extraction from text-based PDFs.
- OCR fallback only for scanned PDFs; keep it optional if time is limited.
- Validate file type by inspecting content, not filename or browser MIME alone.

### Automation
- Playwright Python for the controlled demo application portal only.
- Use role/label/text locators and explicit assertions. Do not rely on fragile long CSS/XPath chains.

### Testing and quality
- Backend: pytest, httpx TestClient, Ruff, mypy or pyright if configured.
- Frontend: Vitest, React Testing Library, ESLint, TypeScript strict mode.
- E2E: Playwright.
- Pre-commit optional if time permits.

## Why this stack
- One Python backend supports API, RAG, document parsing, eligibility, and automation.
- Supabase reduces infrastructure setup and provides Postgres, Auth, Storage, and pgvector.
- React + TypeScript provides a maintainable UI without a heavy framework migration.
- Direct Gemini SDK calls keep the LLM layer understandable and reduce framework overhead.
- A modular monolith is easier for a two-person team to finish and debug than microservices.

## Avoid for this MVP
- Kubernetes, microservices, Kafka, Redis, Celery, and separate vector DB unless a measured need exists.
- Multiple LLM providers at once.
- An agent framework solely for appearance.
- Unpinned dependency versions.
- Deprecated Gemini SDKs or obsolete model IDs.
