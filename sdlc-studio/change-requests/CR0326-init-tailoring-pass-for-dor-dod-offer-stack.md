# CR-0326: init tailoring pass for DoR/DoD: offer stack/profile-derived criteria at project init (RFC0043 slice 3)

> **Status:** Complete
> **Decomposed-into:** EP0067
> **Parent:** RFC0043
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/help/init.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; RFC triage decisions, filed by Claude Fable 5

## Summary

RFC0043 slice 3 (D3: defaults + init tailoring, operator-decided): init copies the shipped DoR/DoD defaults and OFFERS a tailoring pass derived from the project's detected stack/profile (language, test framework, deploy surface) - proposed criteria the operator accepts or edits; the static documents remain the source of truth afterwards. Offer, never auto-apply (the persona team-gen pattern).

## Impact

A new project inherits generic defaults; the ready/done bar that fits a Python CLI differs from a web service, and hand-tailoring is the step everyone skips.

## Acceptance Criteria

- [ ] init writes the default documents and prints the tailoring offer with detected-stack-derived suggestions; nothing is applied without acceptance
- [ ] The tailored result passes slice 1's registry validation (only registered check ids)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
