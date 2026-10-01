# BG0876: npm audit reports brace-expansion and markdown-it advisories in the dev lockfile

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** package.json, package-lock.json, tools/tests/test_lean_dev_advisories_patched.py
> **Evidence:** BG0866 QA review (RUN-01M3VF2J), npm audit at 9f992b78 and f0b63780
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T16:04:38Z

## Summary

npm audit on package-lock.json reports brace-expansion 4.0.0-5.0.11 (high: GHSA-q2hr-2g5m-vwhr, GHSA-qhr7-859c-m2p7, GHSA-6j4f-fj2g-mc7p) and markdown-it <14.3.1 (moderate: GHSA-253c-mchw-3w2r), both reached through markdownlint-cli. BG0033 is Closed and BG0468 Fixed, so nothing open records them. BG0866 held js-yaml the same way.

## Steps to Reproduce

1. npm ci. 2. npm audit -> 2 vulnerabilities (brace-expansion high, markdown-it moderate).

## Proposed Fix

Hold both at patched versions with npm overrides, as BG0866 did for js-yaml, and pin the lockfile with a test that npm audit reports none.

## Acceptance Criteria

### AC1: the dev lockfile resolves patched brace-expansion and markdown-it

- **Given** this repository's `package-lock.json`
- **When** the test reads every `brace-expansion` and `markdown-it` entry in it
- **Then** no `brace-expansion` entry falls in 4.0.0-5.0.11 and every `markdown-it` entry is at 14.3.1 or later, and `package.json` holds the override that pins each
- **Verify:** pytest tools/tests/test_lean_dev_advisories_patched.py::DevAdvisoriesPatchedTests::test_the_lockfile_resolves_patched_brace_expansion_and_markdown_it
- **Verified:** yes (2026-10-01)
- **Fails-on:** the lockfile at 9f992b78, which resolves brace-expansion in 4.0.0-5.0.11 and markdown-it below 14.3.1

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (orchestrator) | Groomed mid-run: premise executed by the BG0866 reviewer (npm audit), one criterion with a Verify selector |
