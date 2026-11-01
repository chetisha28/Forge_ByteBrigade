# 12 — Application Preparation Agent

## Scope
The agent prepares an application draft and demonstrates form filling on a controlled demo portal. It does not submit real government applications in the MVP.

## Workflow
1. User selects a scheme.
2. Backend loads the verified application field mapping.
3. Agent gathers only missing fields.
4. Agent uses confirmed profile/document facts.
5. Agent creates a draft and shows a review screen.
6. User explicitly approves the demo fill.
7. Playwright opens the controlled demo portal.
8. It fills fields using accessible labels/roles.
9. It captures a screenshot or structured completion summary.
10. It stops before final submission and returns the draft to the user.

## Guardrails
- Never navigate to arbitrary user-supplied URLs.
- Allowlist the demo portal origin.
- Do not bypass CAPTCHA, OTP, login, access controls, or anti-bot measures.
- Do not store credentials.
- Do not click final submit on a real government portal.
- Require explicit user approval before any browser action that changes data.
- Do not claim submission or official tracking number without portal confirmation.
- Log actions without logging sensitive field values.
- If the portal structure changes, stop safely and report failure.

## Implementation
For the MVP, create a local/demo form that mimics the structure of a government application but is clearly marked “CivicPilot demo — not an official portal”.
Use Playwright locators based on labels and roles. Add assertions after filling. Avoid brittle CSS/XPath selectors.
