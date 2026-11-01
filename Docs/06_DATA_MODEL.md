# 06 — Data Model

Use UUID primary keys, UTC timestamps, foreign keys, and migrations. Add indexes for common filters and ownership checks.

## Tables

### `profiles`
- `id` UUID PK; references authenticated user ID.
- `full_name` nullable.
- `state_code` nullable.
- `education_level` nullable.
- `course` nullable.
- `study_year` nullable.
- `institution_name` nullable.
- `annual_family_income` nullable numeric.
- `category` nullable; collect only if required for a scheme.
- `created_at`, `updated_at`.

### `schemes`
- `id` UUID PK.
- `slug` unique.
- `name`.
- `summary`.
- `description`.
- `scheme_type` (scholarship initially).
- `state_code` nullable; `central_or_state`.
- `benefit_summary` nullable.
- `official_url`.
- `application_url` nullable.
- `deadline` nullable; never infer a date.
- `status` (active, inactive, verification_required).
- `last_verified_at`.
- `created_at`, `updated_at`.

### `scheme_rules`
- `id` UUID PK.
- `scheme_id` FK.
- `rule_key`.
- `operator` (eq, neq, lt, lte, gt, gte, in, not_in, exists).
- `expected_value` JSONB.
- `required` boolean.
- `source_document_id` FK nullable.
- `source_section` nullable.
- `created_at`, `updated_at`.

### `source_documents`
- `id` UUID PK.
- `scheme_id` FK.
- `title`.
- `source_url`.
- `storage_path` or controlled external URL.
- `document_type`.
- `published_at` nullable.
- `retrieved_at`.
- `last_verified_at`.
- `content_hash`.
- `processing_status`.
- `created_at`.

### `document_chunks`
- `id` UUID PK.
- `source_document_id` FK.
- `scheme_id` FK.
- `chunk_index`.
- `content`.
- `page_number` nullable.
- `section_title` nullable.
- `embedding` vector(768) if using 768-dimensional embeddings.
- `created_at`.
- Unique `(source_document_id, chunk_index)`.

### `user_documents`
- `id` UUID PK.
- `user_id` FK.
- `storage_path`.
- `original_filename` (display only; never use as storage key).
- `detected_type`.
- `file_size`.
- `processing_status`.
- `extracted_fields` JSONB nullable.
- `user_confirmed_fields` JSONB nullable.
- `created_at`, `updated_at`.

### `application_drafts`
- `id` UUID PK.
- `user_id` FK.
- `scheme_id` FK.
- `status` (draft, ready_for_review, approved_for_demo, demo_completed, failed).
- `form_data` JSONB.
- `automation_log` JSONB nullable.
- `created_at`, `updated_at`.

## Important data rules
- Store only data necessary for the user journey.
- Keep sensitive category/income fields optional unless a selected scheme needs them.
- Never store raw document contents in logs.
- Never use an LLM-generated value as a confirmed profile fact without user review.
- Store provenance for every eligibility rule and factual scheme field.
- Add Row Level Security (RLS) for user-owned records and private storage objects.
- Do not expose service-role keys to the browser.
