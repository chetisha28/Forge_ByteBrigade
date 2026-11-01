# CivicPilot — Antigravity Documentation Pack

This folder is the source of truth for building CivicPilot. Read the files in this order before making architectural changes.

## Required reading order
1. `01_PRODUCT_BRIEF.md`
2. `02_MVP_SCOPE_AND_PRIORITIES.md`
3. `03_AI_LOOK_AND_FEEL_QUALITY_RULES.md`
4. `04_TECH_STACK.md`
5. `05_SYSTEM_ARCHITECTURE.md`
6. `06_DATA_MODEL.md`
7. `07_API_CONTRACT.md`
8. `08_RAG_AND_GOVERNMENT_DATA.md`
9. `09_ELIGIBILITY_ENGINE.md`
10. `10_DOCUMENT_SECURITY_AND_PRIVACY.md`
11. `11_UI_UX_SPECIFICATION.md`
12. `12_APPLICATION_AGENT.md`
13. `13_TESTING_AND_ACCEPTANCE.md`
14. `14_CLEANUP_COMMAND.md`
15. `15_ENVIRONMENT_AND_DEPLOYMENT.md`
16. `16_IMPLEMENTATION_PLAN.md`
17. `17_ANTIGRAVITY_MASTER_INSTRUCTIONS.md`

## Non-negotiable rules
- Treat these documents as project requirements, not suggestions.
- Inspect the existing repository before changing it. Preserve working code.
- Do not invent government scheme details, eligibility rules, benefits, dates, or application outcomes.
- Never expose secrets in frontend code or commit `.env` files.
- Do not claim that an application was submitted unless an official portal confirms it.
- Build a small, complete, tested workflow before adding optional features.
- Keep the product specific to citizen services; do not turn it into a generic chatbot template.
- Ask before making destructive, irreversible, or scope-changing changes.

## Project positioning
CivicPilot is an AI-assisted government scheme discovery and application-preparation platform. Its first vertical is student scholarships in India. It is not an official government service and must clearly say so.
