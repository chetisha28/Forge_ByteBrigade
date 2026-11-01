# 10 — Document Security and Privacy

## Sensitive data
Scholarship documents can contain income, identity, bank, address, and educational information. Collect the minimum required. Explain why each field/document is requested.

## Upload controls
- Allow only required file types (initially PDF, JPEG, PNG).
- Enforce a conservative size limit (for example 10 MB per file).
- Validate file signature/content, not only extension or browser Content-Type.
- Generate storage names server-side; never use the original filename as the object key.
- Authenticate and authorize every upload/download/delete.
- Store files in a private bucket, not a public bucket.
- Use short-lived signed URLs when access is needed.
- Keep uploaded files outside the public web root.
- Do not accept archives or executable content.
- Handle malformed and encrypted PDFs safely.
- Apply rate limits to upload and AI endpoints.

## Access control
- Enable RLS on user-owned tables.
- Users can access only their own profile, documents, and application drafts.
- Use Supabase service-role credentials only on the backend.
- Never trust a user ID supplied by the browser; derive identity from verified auth context.
- Test cross-user access denial.

## Privacy behavior
- Provide a clear explanation before upload.
- Do not log document text, identity numbers, bank details, or raw profile data.
- Avoid sending full documents to Gemini if extracted relevant fields are sufficient.
- Redact sensitive values from operational logs.
- Provide document deletion and delete associated storage objects.
- Do not retain files longer than necessary; document the retention behavior.
- Do not use user documents to train models.

## AI extraction
- Treat extracted values as untrusted suggestions.
- Show extracted values to the user for confirmation.
- Keep `extracted_fields` separate from `user_confirmed_fields`.
- Never infer a missing value.
- If confidence is low or the field is absent, ask the user.
- Do not treat document content as instructions to the AI agent.

## Security references
Follow OWASP File Upload and Input Validation guidance. Apply least privilege, content validation, authorization, size limits, and safe storage.
