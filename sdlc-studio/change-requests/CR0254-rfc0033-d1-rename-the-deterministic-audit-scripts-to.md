# CR-0254: RFC0033 D1: rename the deterministic audit scripts to free the audit stem

> **Status:** Proposed
> **Priority:** P2
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py, .claude/skills/sdlc-studio/scripts/audit_check.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py

## Summary

The verb 'audit' is overloaded three ways; RFC0033 (Accepted) frees it for the user-facing adversarial weakness-hunt by renaming the two deterministic scripts. audit.py (sprint pre-flight tranche readiness) -> readiness.py; `audit_check.py` (schema-v3 CI linter) -> `schema_check.py.` Update every call site (gate.py, sprint.py), the tests, and reference-scripts.md. Internal-only - no public command surface. This CR gates the rest of the RFC0033 workstream.

## Impact

No user-facing change; the two commands keep working under new script names. Downstream CRs (the audit command, retiring review generate) depend on this landing first.

**Effort:** M

## Acceptance Criteria

- [ ] audit.py and `audit_check.py` are renamed; no import or call site references the old names; tests pass under the new names. Verify: test ! -f .claude/skills/sdlc-studio/scripts/audit.py && test -f .claude/skills/sdlc-studio/scripts/readiness.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
