# 05 — System Architecture

## Architecture style
Use a modular monolith. One FastAPI application with clearly separated modules. One PostgreSQL database. One React frontend.

## Logical architecture

```text
React + TypeScript (Vite)
  ├── Public landing pages
  ├── Profile and dashboard
  ├── Scheme discovery/details
  ├── AI assistant
  ├── Document center
  └── Application preparation
          |
          | HTTPS / JSON / multipart upload
          v
FastAPI
  ├── API routers
  ├── Authentication/authorization dependencies
  ├── Profile service
  ├── Scheme catalog service
  ├── Eligibility rules engine
  ├── Document ingestion service
  ├── RAG retrieval and answer service
  ├── Application preparation service
  └── Playwright demo adapter
          |
          v
Supabase PostgreSQL
  ├── users/profiles
  ├── schemes and eligibility rules
  ├── source documents and chunks
  ├── embeddings (pgvector)
  ├── user document metadata
  └── application drafts
          |
          +--> Supabase Storage (private bucket)
          |
          +--> Gemini API (generation + embeddings)
```

## Module boundaries
- `auth`: verify identity and user ownership.
- `profiles`: validated user profile data.
- `schemes`: official scheme catalog and provenance.
- `eligibility`: deterministic rule evaluation; no LLM as final authority.
- `documents`: upload, validation, extraction, confirmation.
- `rag`: chunking, embedding, retrieval, grounded response.
- `applications`: draft preparation and review state.
- `automation`: restricted Playwright adapter for the demo portal.

## Key design decisions
1. All business rules live in backend services, not React components.
2. All model calls go through one AI service module.
3. Scheme facts are stored as structured data with source metadata.
4. LLM answers must use retrieved evidence and cite it.
5. User documents are private and accessible only to their owner.
6. User-provided profile facts and AI-extracted facts must be distinguishable.
7. Application submission is not in the MVP. Demo automation only fills a controlled portal and stops before final submission.
8. Use background jobs only if processing latency requires them; don't add a queue pre-emptively.

## Failure behavior
- Gemini unavailable: show a clear retry message; core scheme browsing and eligibility rules should remain usable.
- Embedding failure: do not mark ingestion as complete.
- PDF extraction failure: show a document-specific error; do not invent extracted content.
- Storage failure: do not create a successful document record.
- Unknown eligibility field: return `needs_information`, not false.
- Browser automation failure: preserve the draft and show which step failed.
