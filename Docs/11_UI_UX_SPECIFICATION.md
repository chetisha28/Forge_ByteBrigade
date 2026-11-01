# 11 — UI/UX Specification

## Overall experience
A calm, dependable citizen-service tool. The UI should emphasize clarity, provenance, and next steps rather than visual spectacle.

## Primary navigation
- Overview
- Find schemes
- AI assistant
- My documents
- Applications

Keep navigation short. Do not create routes that have no real content.

## Required screens

### 1. Landing page
- Clear explanation of the service.
- Primary CTA: “Find scholarships”.
- Secondary CTA: “See how it works”.
- Explain that CivicPilot is independent and not a government website.
- No fake partner logos, user counts, testimonials, or claims.

### 2. Profile setup
- Ask only for fields needed to discover scholarships.
- Explain why income/category/state fields may be requested.
- Allow “Prefer not to say” where possible.
- Use progressive disclosure rather than one intimidating form.
- Validate fields and explain errors.

### 3. Dashboard
- Show saved profile completeness only if computed.
- Show recommended schemes based on actual data.
- Show document/action reminders only when they exist.
- Avoid fake statistics and decorative charts.

### 4. Scheme discovery
- Search and filters.
- Scheme name, issuing authority, state/central scope, benefit summary, deadline only if verified, source verification date.
- Show “Potential match” rather than guaranteed eligibility.
- Explain the reason for recommendation.

### 5. Scheme detail
- Overview.
- Eligibility criteria.
- Benefits.
- Required documents.
- Application process.
- Official links and source documents.
- Last verified date and source freshness warning.

### 6. AI assistant
- Scheme-aware conversation.
- Source citations adjacent to claims.
- “Not enough information in the official documents” state.
- Follow-up prompts only when relevant.
- No fake typing delays or fabricated sources.

### 7. Document center
- Drag/drop and browse upload.
- Allowed file types and size shown before upload.
- Upload progress based on actual transfer.
- Extraction preview with editable values.
- User confirmation step.
- Delete action.

### 8. Eligibility result
- Outcome: potentially eligible / not eligible / needs information.
- Rule-by-rule breakdown.
- Source for each criterion.
- Clear next step.
- Informational disclaimer.

### 9. Application preparation
- Draft fields populated from confirmed facts only.
- Missing fields clearly highlighted.
- Review before automation.
- Controlled demo form only.
- Stop before final submit.

## Responsive behavior
- Mobile first for forms and scheme cards.
- Desktop can use a wider content layout and side-by-side evidence panels.
- Tables should become readable stacked sections or horizontally scrollable with labels on mobile.
- Avoid fixed-width layouts and overflow.

## Accessibility
- Semantic HTML.
- Visible keyboard focus.
- Labels for every input.
- Accessible error announcements.
- Sufficient contrast.
- Reduced-motion support.
- Do not communicate status by color alone.
