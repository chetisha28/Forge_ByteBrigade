# 14 — Project Cleanup Command

## Purpose
Provide an explicit command that audits and removes safe, known generated artifacts. It must not destructively rewrite application code or delete user data.

## Required commands
At repository root:
- `npm run cleanup` — dry-run only; prints what would be removed.
- `npm run cleanup:apply` — removes only approved safe artifacts after explicit invocation.
- `npm run cleanup:report` — produces a report of suspicious leftovers and possible unused code; does not delete them.

If the repository is not an npm workspace, expose equivalent commands through `Makefile` or documented Python CLI. Do not create duplicate command systems.

## Safe automatic cleanup targets
Only remove when inside the repository and not symlinks:
- `.DS_Store`
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.coverage`
- `htmlcov/`
- `coverage/`
- `playwright-report/`
- `test-results/`
- frontend build output such as `dist/` (only when confirmed as generated build output)
- temporary files created by known project tooling.

## Never automatically delete
- Source files, routes, components, migrations, tests, fixtures, seed data, docs, assets, or user uploads.
- `.env` or any environment file.
- Lockfiles or dependency manifests.
- `node_modules`, virtual environments, or package caches by default.
- Files merely because they appear unused.
- Comments, TODOs, or code blocks without human review.
- Files outside the repository root.
- Symlink targets.

## “AI-generated leftovers” audit
The report may flag:
- unused imports and variables (using lint/type tooling).
- unreachable or unreferenced modules (as suggestions only).
- commented-out code blocks.
- TODO/FIXME/debug prints and console logs.
- duplicated components or styles.
- placeholder copy, lorem ipsum, fake data, and dead links.
- suspiciously generic or repeated UI components.
- broad exception handlers and swallowed errors.
- unused dependencies.

Do not auto-delete these based on text matching. Produce a report with file path, line, reason, and recommended human action.

## Safety implementation
- Resolve and validate repository root before deleting anything.
- Refuse to run if root is filesystem root, home directory, or outside expected project.
- Do not follow symlinks.
- Default to dry-run.
- Print every target before deletion.
- Require `--apply` for deletion.
- Never use broad shell commands such as `rm -rf *`, `git clean -xfd`, or wildcard deletion.
- Preserve exit codes and report failures.
- Add unit tests for path containment and allowlist behavior.

## Suggested CLI behavior
`python scripts/cleanup.py --dry-run`
`python scripts/cleanup.py --apply`
`python scripts/cleanup.py --report`

## Implementation notes
- Keep the allowlist in one explicit configuration section.
- Keep the audit separate from deletion.
- Do not install new dependencies just for cleanup if standard library is sufficient.
- Add the root package scripts only after inspecting the existing package manager and scripts.
- Cleanup must never modify tracked source code automatically.
