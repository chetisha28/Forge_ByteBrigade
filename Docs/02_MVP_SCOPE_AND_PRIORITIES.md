# 02 — MVP Scope and Priorities

## P0 — Must work
- Responsive React application with working navigation.
- Student profile creation/editing.
- Seeded, source-verified scholarship dataset (start with 10–20).
- Scheme list, filters, and detail pages.
- Rule-based eligibility assessment with “eligible / not eligible / needs information” outcomes.
- RAG chat over the selected scheme's official source documents.
- Citations that open the correct source document or official URL.
- Useful loading, empty, error, and retry states.
- Basic automated tests.

## P1 — Build if P0 is stable
- Private document upload.
- Text extraction from PDF.
- Structured extraction preview requiring user confirmation.
- Missing-document checklist.
- Application preparation form populated from confirmed profile data.
- Demo portal form-fill automation.

## P2 — Only if time remains
- Hindi/Gujarati interface and responses.
- OCR for scanned certificates.
- More scheme categories.
- Saved application drafts and progress history.
- More advanced agent orchestration.

## Explicitly do not build
- Fake “live government integration”.
- Fake success notifications or application receipts.
- Unverified “AI match percentage” presented as an official score.
- A large admin panel unless needed to manage the seed dataset.
- A generic AI chat product unrelated to schemes.
- Unnecessary microservices, Redis, Kubernetes, or a separate vector database.

## Scope rule
If a feature cannot be implemented, tested, and demonstrated end-to-end before the deadline, mark it as deferred. Do not create a non-functional UI placeholder and call it complete.
