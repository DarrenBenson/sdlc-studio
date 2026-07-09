# BG0096: CI never runs gate.py although the pre-commit hook and CONTRIBUTING claim parity

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (CI hardening; local gates currently read green). .githooks/pre-commit:78-80 says 'This is the same gate CI runs' and CONTRIBUTING.md:83-84 says 'CI re-runs the same gate on push' - but .github/workflows/lint.yml:30-54 runs npm lint, npm test, coverage and bandit only; no gate.py step exists (verified: grep gate.py lint.yml -> 0), and npm run lint also omits lint:disclosure (package.json). With hook enablement opt-in per clone (and unset in this clone, see the lint bug), artefact drift/conformance/integrity breakage can reach main with CI green; two docs assert a parity that does not exist. Found by RV0007.

## Steps to Reproduce

grep -n 'gate.py' .github/workflows/lint.yml -> no matches; compare .githooks/pre-commit:78 and CONTRIBUTING.md:83.

## Proposed Fix

Add a 'python3 .claude/skills/sdlc-studio/scripts/gate.py --root .' step to lint.yml after setup-python (or correct both docs).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
