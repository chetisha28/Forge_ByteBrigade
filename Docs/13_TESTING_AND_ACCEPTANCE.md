# 13 — Testing and Acceptance Criteria

## Backend tests
- Profile validation and update.
- Scheme filtering and pagination.
- Eligibility pass/fail/missing-information cases.
- RAG citation mapping.
- RAG insufficient-evidence behavior.
- File type and size validation.
- Ownership and authorization checks.
- Application draft state transitions.
- Agent allowlist and stop-before-submit behavior.

## Frontend tests
- Profile form validation.
- Scheme search/filter interactions.
- Scheme details and source links.
- Chat loading/error/answer/citation states.
- Upload validation and extraction confirmation.
- Eligibility outcome states.
- Application review and approval.

## End-to-end demo scenario
1. Create a student profile.
2. Find relevant seeded scholarships.
3. Open one scholarship.
4. Ask a factual question about income or documents.
5. Verify that answer cites the official source.
6. Run eligibility check.
7. Upload a sample PDF.
8. Review extracted fields.
9. Prepare an application draft.
10. Approve demo automation.
11. Verify the demo portal fields were populated and no final submission occurred.

## Definition of done
- All P0 flows work from browser to database.
- No dead visible controls.
- No uncaught errors in normal flows.
- No secrets in frontend bundle or repository.
- RLS and ownership checks tested.
- Citations resolve to real sources.
- No unsupported claims about eligibility or submission.
- Responsive layout tested at mobile and desktop widths.
- Lint, typecheck, and test commands pass.
- README setup steps work on a clean checkout.

## Demo data
Use clearly labelled sample users and sample documents. Never use real citizens' identity or bank documents in screenshots or demo recordings.
