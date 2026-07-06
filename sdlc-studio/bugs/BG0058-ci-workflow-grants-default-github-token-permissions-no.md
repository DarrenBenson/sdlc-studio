# BG0058: CI workflow grants default GITHUB_TOKEN permissions: no permissions block in lint.yml

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

Neither job in the CI workflow declares a `permissions:` block, so the workflow's
`GITHUB_TOKEN` runs at the repository/organisation default. The steps only check out and run
linters/tests; nothing needs write access.

Weakness class: CWE-250 (execution with unnecessary privileges), least-privilege gap.
Remediation-only.

## Evidence

- `.github/workflows/lint.yml:1-12` - no top-level or job-level `permissions:` key on either
  the `ci` or `windows-smoke` job. Confirmed by reading the full file: steps run `npm ci`,
  `npm run lint`, `npm test`, coverage, and bandit; none writes to the repo.

## Impact

If the repository or organisation default is the legacy permissive token, every step
(including `npm ci`-installed third-party code such as markdownlint's dependency tree) runs
with a token that can write to the repo. A compromised npm transitive dependency could push
or tamper with releases.

## Steps to Reproduce

Not recorded (remediation-only). Evidenced by the absent `permissions:` key.

## Proposed Fix

Add `permissions: contents: read` at the workflow top level in `lint.yml`.

## Open Question

Whether the repository/organisation GitHub settings already restrict the default token to
read-only (would downgrade this to Low). Fix is cheap and definitive regardless.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; filed from RV0006 security leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
