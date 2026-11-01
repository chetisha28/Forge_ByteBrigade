# 07 — API Contract

Prefix all endpoints with `/api/v1`. Use JSON responses with consistent error shapes. Validate every request with Pydantic.

## Profile
- `GET /profiles/me` — fetch current user's profile.
- `PUT /profiles/me` — create/update profile.

## Schemes
- `GET /schemes` — list and filter schemes (`q`, `state`, `type`, `status`, `page`, `page_size`).
- `GET /schemes/{scheme_id}` — scheme detail including source references.
- `POST /schemes/recommendations` — return candidate schemes for current profile.

## Eligibility
- `POST /schemes/{scheme_id}/eligibility-check` — evaluate profile and optional user-confirmed document facts.
- Response includes `status`, `matched_rules`, `failed_rules`, `missing_fields`, `explanation`, and `sources`.

Possible status values:
- `potentially_eligible`
- `not_eligible`
- `needs_information`
- `not_assessed`

Never return a fabricated numeric match score as if it were an official score.

## RAG assistant
- `POST /assistant/query`
- Request: `scheme_id`, `question`, optional `conversation_id`.
- Response: `answer`, `citations[]`, `insufficient_evidence`, `conversation_id`.
- Each citation includes `source_document_id`, `title`, `page_number` if known, `source_url`, and a short supporting excerpt.

## User documents
- `POST /documents` — multipart upload.
- `GET /documents` — list current user's documents.
- `GET /documents/{document_id}` — status and confirmed extraction fields.
- `POST /documents/{document_id}/confirm-extraction` — user confirms or corrects extracted fields.
- `DELETE /documents/{document_id}` — delete metadata and storage object.

## Application preparation
- `POST /applications/drafts` — create draft.
- `GET /applications/drafts` — list current user's drafts.
- `GET /applications/drafts/{draft_id}` — retrieve draft.
- `PATCH /applications/drafts/{draft_id}` — update fields.
- `POST /applications/drafts/{draft_id}/prepare-demo` — run restricted demo fill.
- No production submit endpoint in the MVP.

## Error format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Please correct the highlighted fields.",
    "details": []
  }
}
```

## API rules
- Use correct HTTP status codes.
- Return 401 for unauthenticated requests and 403 for unauthorized access.
- Return 404 for resources not owned by the user where appropriate to avoid leaking existence.
- Add pagination for list endpoints.
- Never return stack traces or secrets.
- Document endpoints with FastAPI OpenAPI.
