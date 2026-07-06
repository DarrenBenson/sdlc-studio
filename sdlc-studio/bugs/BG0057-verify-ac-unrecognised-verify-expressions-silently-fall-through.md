# BG0057: verify_ac unrecognised Verify expressions silently fall through to shell execution

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

Any Verify expression whose head is not a recognised DSL verb falls through to shell
execution rather than erroring. Combined with BG0056, an attacker-controlled line need not
even name a DSL verb to be executed.

Weakness class: CWE-78 / CWE-1188 (insecure default behaviour). Remediation-only.

## Evidence

- `.claude/skills/sdlc-studio/scripts/verify_ac.py:306-309` - fallback `return "shell", expr`
  for any expression whose head is not a DSL verb ("Fallback: treat the whole expression as a
  shell command").
- `verify_ac.py:224-239` - `lint_verifier` flags some of these but is advisory only and only
  when `verify_ac.py lint` is run.

## Impact

Widens the executable surface: any stray prose or typo'd line matching the `Verify:` regex
becomes a shell command run with a 120 s timeout. Together with the ingestion path in BG0056
this removes the need for an attacker-controlled line to name a shell verb explicitly.

## Steps to Reproduce

Not recorded (remediation-only). Evidenced by the fallback branch and the advisory-only lint.

## Proposed Fix

Make the fallback opt-in: require the explicit `shell` verb for shell execution, and turn an
unrecognised head into an "invalid verifier" failure (kind=invalid, exit 2). Keep the current
behaviour available behind a config flag for backwards compatibility.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; filed from RV0006 security leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
