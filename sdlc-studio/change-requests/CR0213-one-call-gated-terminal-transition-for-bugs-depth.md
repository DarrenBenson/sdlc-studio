# CR-0213: one-call gated terminal transition for bugs: depth + verdict + status together

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Closing a fixed bug is a three-verb ceremony (transition annotate --field 'Verification depth', critic record, transition set --status Fixed) that is easy to half-do: BG0093 reached the Fixed gate un-stamped this sprint purely because the depth stamp is a separate call from the transition. artifact close orchestrates this for the close verb, but the common transition path has no equivalent.

## Acceptance Criteria

- [ ] transition set accepts --depth (and optionally --verdict/--reviewer/--author) and performs stamp + record + gated transition atomically, refusing everything if any part fails
- [ ] The existing separate verbs keep working; reference-scripts and help documents name the one-call form as the canonical bug-fix path

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
