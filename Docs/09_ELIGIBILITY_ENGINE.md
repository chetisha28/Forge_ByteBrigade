# 09 — Deterministic Eligibility Engine

## Core principle
Use deterministic backend rules for eligibility. Use Gemini only to explain the outcome in plain language, never to decide the final outcome.

## Inputs
- Confirmed profile fields.
- User-confirmed document extraction fields.
- Structured scheme rules with source provenance.

## Evaluation outcomes
- `potentially_eligible`: all required rules evaluated and passed.
- `not_eligible`: at least one verified hard rule failed.
- `needs_information`: one or more required fields are missing or uncertain.
- `not_assessed`: no reliable rules exist for the scheme.

## Rule representation
Example:
```json
{
  "rule_key": "annual_family_income",
  "operator": "lte",
  "expected_value": 250000,
  "required": true,
  "source_section": "Eligibility, paragraph 2"
}
```

## Evaluation behavior
- Missing values are not treated as zero or false.
- Unknown criteria produce `needs_information`.
- Conflicting sources produce a visible warning and manual review state.
- Do not infer caste/category, disability, domicile, income, or other sensitive facts.
- Do not silently round values in a way that changes the outcome.
- Store the rules and source used for each assessment.
- Re-run assessment when profile or scheme rules change.

## UI explanation
Show:
- Outcome label.
- Rules passed.
- Rules not met.
- Information still needed.
- Source for each rule.
- Disclaimer that the result is an informational pre-check, not an official decision.

Do not display a “92% eligible” score unless a defensible, documented scoring model exists and the UI clearly labels it as a non-official relevance indicator.
