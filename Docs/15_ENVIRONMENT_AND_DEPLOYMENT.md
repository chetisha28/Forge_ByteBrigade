# 15 — Environment and Deployment

## Environment variables
Backend `.env` (never commit):
- `APP_ENV`
- `APP_NAME`
- `FRONTEND_ORIGIN`
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` (server use only if required)
- `SUPABASE_SERVICE_ROLE_KEY` (backend only; highly restricted)
- `SUPABASE_STORAGE_BUCKET`
- `GEMINI_API_KEY`
- `GEMINI_GENERATION_MODEL`
- `GEMINI_EMBEDDING_MODEL`
- `GEMINI_EMBEDDING_DIMENSIONS`
- `JWT`/auth verification configuration only if needed by chosen Supabase auth integration.

Frontend `.env`:
- `VITE_API_BASE_URL`
- Supabase public URL/anon key only if frontend directly uses Supabase Auth.
Never place service-role keys, Gemini API keys, or database credentials in `VITE_*` variables.

## Deployment sequence
1. Create Supabase project.
2. Enable pgvector extension.
3. Apply Alembic migrations.
4. Create private storage bucket and storage policies.
5. Seed verified schemes and source documents.
6. Deploy FastAPI backend.
7. Configure CORS for the exact frontend origin.
8. Deploy frontend.
9. Configure environment variables in hosting dashboards.
10. Run smoke tests against deployed endpoints.
11. Verify auth, RLS, uploads, citations, and demo automation.

## Operational requirements
- Use HTTPS.
- Restrict CORS to known origins.
- Add health endpoint `/health`.
- Log request IDs and operational errors, not sensitive user data.
- Add timeouts and bounded retries for Gemini calls.
- Set rate limits on expensive AI and upload endpoints.
- Keep secrets in deployment secret stores.
- Pin dependencies and use lockfiles.
- Provide a rollback path for database migrations and deployment.

## Local setup
Document exact commands for frontend and backend after repository structure is created. Include `.env.example` with placeholders only.
