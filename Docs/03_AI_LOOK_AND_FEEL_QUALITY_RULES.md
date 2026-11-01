# 03 — Product Quality: Avoiding Generic AI-Generated Design and Code

## Principle
The goal is not to hide that AI tools were used. The goal is to ship a coherent, specific, reviewed product. Avoid generic or unfinished patterns regardless of who wrote the code.

## Visual patterns to avoid when they are not justified
- Default purple/blue gradient backgrounds across every section.
- Gradient text on every heading.
- Repeated three-card feature rows with identical icon/title/description structure.
- The same rounded card nested inside another rounded card.
- Excessive glassmorphism, blur, glow, neon borders, and floating blobs.
- Emoji used as the main icon system.
- Decorative charts, fake metrics, fake testimonials, fake partner logos, or invented user counts.
- Generic hero copy such as “Unlock the power of AI” or “Revolutionize your journey”.
- A huge centered hero with meaningless buttons and an irrelevant logo strip.
- Random illustrations that do not explain a real workflow.
- Overuse of badges, pills, shadows, and gradients.
- Every page having the same layout regardless of its content.

These are not universally forbidden design choices. Use them only when they serve a clear purpose and are consistent with the rest of the product.

## CivicPilot-specific design direction
- Make the product feel like a reliable public-service utility, not an AI startup landing-page template.
- Use a restrained, accessible palette: warm neutral surfaces, dark ink text, and one deliberate accent color. Use status colors only for meaningful states.
- Use typography with a clear hierarchy and comfortable reading widths.
- Prioritize scheme names, eligibility requirements, deadlines, source provenance, and next actions.
- Use real information density where useful: comparison tables, checklists, filters, document status, and source panels.
- Use icons consistently from one icon set. Do not mix emoji, random SVGs, and unrelated icon styles.
- Use the supplied CivicPilot visual reference as a direction, not as a reason to reproduce inaccurate labels or fake data.
- Design for mobile and keyboard use, not just a desktop screenshot.

## Content rules
- No lorem ipsum, fake people, fake testimonials, fabricated statistics, or invented government endorsements.
- No placeholder text in a “finished” screen.
- Use realistic demo data clearly labelled as demo data.
- Avoid exaggerated claims such as “100% accurate”, “guaranteed eligibility”, “instant approval”, or “AI does everything”.
- Use concise, plain language. Explain technical terms only when needed.
- Every scheme fact must have a source and verification date.
- Do not present model-generated content as an official government statement.

## Interaction and completeness rules
- Every visible button, link, tab, filter, and form control must work or be visibly disabled with an explanation.
- No dead buttons, fake progress bars, arbitrary loading delays, or non-functional toggles.
- Provide loading, empty, error, success, and validation states for important flows.
- Forms must show field-level errors and preserve user input after recoverable errors.
- Use confirmations for destructive actions and sensitive submissions.
- Use accessible labels, focus states, semantic HTML, and sufficient contrast.
- Avoid excessive animation; respect reduced-motion preferences.

## Code quality rules for AI-assisted implementation
- Do not create unnecessary abstractions, wrapper components, factories, hooks, services, or files.
- Do not duplicate business logic between frontend and backend.
- Do not add comments that merely restate the code.
- Keep comments only for non-obvious reasoning, constraints, security decisions, or tricky algorithms.
- Remove stale TODOs, commented-out code, debug prints, console logs, and unused imports after verifying they are not needed.
- Do not suppress type errors or lint warnings with broad ignores to make checks pass.
- Do not use `any` or `dict[str, Any]` everywhere when a proper schema is possible.
- Do not swallow exceptions or return fake successful responses.
- Do not hardcode secrets, URLs, IDs, eligibility limits, or dates in UI components.
- Do not use mock data in production paths. Keep fixtures and demo data clearly separated.
- Prefer small, readable functions and explicit data flow over clever abstractions.
- Follow the repository's existing conventions unless there is a documented reason to change them.

## Review checklist before declaring a page complete
- Does the content belong specifically to CivicPilot?
- Are all facts and claims supportable?
- Are all controls functional?
- Are empty, loading, error, and success states present?
- Does the layout work at mobile, tablet, and desktop widths?
- Is keyboard navigation possible?
- Is there any redundant card, icon, gradient, animation, or copy?
- Is there any fake data that could mislead a user?
- Can the page be understood without an explanation from the developer?
