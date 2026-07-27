# CR-0446: Replace the falsified token-observation premise in the seven copies outside the TRD

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/../reference-config.md, .claude/skills/sdlc-studio/scripts/../reference-sprint.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (scope residue from the D0069 cap); agent; skill v5.0.0

## Summary

US0459 repairs the TRD and the D0020 row that CR0431 names. The same falsified premise - that a script cannot observe token spend, contradicted by `run_state.session_tokens` - is asserted in roughly seven further shipped files.

## Impact

Who: any consuming project reading the shipped payload, which states a limitation the code does not have. What breaks: a reader designs around an absent capability, and the premise keeps justifying decisions it no longer supports.

## Acceptance Criteria

- [ ] Every live assertion of the premise outside the TRD is replaced with the measured position or removed.
- [ ] The sweep enumerates its targets by searching the tracked tree rather than from a list, so a copy nobody remembered is still found.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (scope residue from the D0069 cap) | Raised |
