# 16 — Implementation Plan for a Two-Person, Less-than-One-Week Team

## Day 1 — Repository, data, schema
- Inspect repository and preserve existing working files.
- Create app structure and configuration.
- Create Supabase project and database schema.
- Gather 10–20 official scholarship records.
- Record sources, dates, eligibility rules, and required documents.
- Seed structured scheme data.

## Day 2 — Core backend and eligibility
- Implement profile endpoints.
- Implement scheme list/detail endpoints.
- Implement deterministic eligibility engine.
- Add tests for missing, passing, and failing criteria.

## Day 3 — RAG
- Ingest official PDFs.
- Extract text and preserve page metadata.
- Chunk and embed.
- Store vectors in pgvector.
- Implement retrieval and grounded answers with citations.
- Test insufficient-evidence behavior.

## Day 4 — Frontend integration
- Landing, profile, dashboard, scheme list/detail.
- Chat with citations.
- Eligibility breakdown.
- Connect all screens to real endpoints.
- Handle loading, empty, and error states.

## Day 5 — Documents and demo agent
- Secure upload and extraction.
- User confirmation of extracted fields.
- Missing-document checklist.
- Application draft.
- Local demo portal and Playwright form fill; stop before submit.

## Day 6 — Hardening and demo
- End-to-end testing.
- Fix high-impact bugs.
- Responsive and accessibility pass.
- Deployment and smoke tests.
- Prepare 3-minute demo and backup recording.

## Team split
Member A: FastAPI, database, eligibility, RAG, document processing, automation.
Member B: React UI, interaction design, API integration, responsive behavior, deployment support.
Both: data verification, test scenarios, security review, final demo.

## Priority rule
If behind schedule, defer OCR and Playwright before sacrificing the working scheme discovery, eligibility, and cited RAG experience.
