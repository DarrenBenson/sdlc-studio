# CR-0342: refine's Draft-story output cannot pass the pre-commit gate: validate flags seeded placeholder ACs as errors regardless of status

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

refine seeds a story's ACs with {{context}}/{{action}}/{{executable check}} placeholders (the documented Draft state - validate is meant to keep flagging until the author makes them executable). But `validate._check_placeholders` flags them as ERRORS regardless of story status, so a freshly-refined Draft story always fails the gate. A large refine (RUN-01KXQH64: 56 stories, ~150 placeholder ACs) then forces either full up-front grooming (speculative ACs for work weeks out) or a --no-verify bypass of the un-skippable gate. The gate cannot distinguish an expected ungroomed Draft story from an invalid artifact.

## Impact

Every bulk refine (decompose-to-design) hits this: the refine commit that CREATES the Draft stories cannot pass the gate the placeholders are meant to keep them from reaching Done, so an operator must groom prematurely or bypass the gate - undermining the un-skippable-gate principle exactly where refine is working as designed.

## Acceptance Criteria

- [ ] validate treats a seeded {{...}} placeholder AC in a non-Ready (Draft) story as a WARNING (not a blocking error), so a refine-only commit lands; the placeholder still blocks the story from reaching Ready/Done (the transition/verify gates unchanged), so nothing ungroomed can be delivered.
- [ ] A Ready or later story with a placeholder AC remains a hard error (a groomed story must have executable ACs).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
