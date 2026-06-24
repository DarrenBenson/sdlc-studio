# CR-0115: Scaffold the test-spec AC Coverage Matrix from an epic stories ACs at design time

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

CR0110 made the design rung author the test-spec AC Coverage Matrix, but nothing scaffolds it: artifact.py new --type test-spec renders only a minimal stub and the core template carries a single placeholder row. So a field agent breaking down EP0005 hand-extracted 47 ACs across 7 stories via grep and transcribed every matrix row by hand. That is laborious and an integrity risk - a missed AC is a silent coverage gap (the exact thing the matrix exists to prevent). Add a deterministic helper that extracts every AC from an epic stories and emits a pre-filled matrix (one row per AC, Story plus AC-id plus title), leaving the Test Cases column blank for the model to map - determinism in the script, judgement in the model.

## Acceptance Criteria

- [ ] a helper (e.g. a verify_ac or test-spec mode) takes an epic and emits an AC Coverage Matrix pre-filled with one row per AC across that epic stories (Story, AC id, Description), Test Cases + Status blank
- [ ] every AC in the epic stories appears as exactly one matrix row - no AC can be silently omitted; the model fills Test Cases + Status, then ts-check (CR0085) validates completeness
- [ ] this removes the manual AC hand-extraction at --goal design (CR0110); documented in reference-test-spec.md + the reference-sprint.md design rung
- [ ] unit test: an epic with N stories totalling M ACs yields a matrix with M rows; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Raised |
