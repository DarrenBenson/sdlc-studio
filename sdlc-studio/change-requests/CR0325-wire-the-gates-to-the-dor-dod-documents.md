# CR-0325: Wire the gates to the DoR/DoD documents: grooming reads the ready bar, Done/close/release read the done bar (RFC0043 slice 2)

> **Status:** In Progress
> **Decomposed-into:** EP0066
> **Parent:** RFC0043
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; RFC triage decisions, filed by Claude Fable 5

## Summary

RFC0043 slice 2: the existing gates READ the project's documents instead of hardcoding the bar. sprint plan's grooming resolves the story-level DoR's tagged checks; transition -> Done and the critic gate resolve the story-level DoD; gate --require-retro resolves the sprint-level DoD (subsuming RFC0042's close-down as its close clause); gate --release resolves the release-level DoD. A project with no documents gets today's behaviour unchanged (the shipped defaults ARE today's bar) - the wiring changes where the bar is DEFINED, not what it defaults to.

## Impact

Without the wiring the documents from slice 1 are advisory prose - and the field evidence on unenforced DoDs is that they are skipped under pressure.

## Acceptance Criteria

- [ ] Each named gate resolves its level's tagged criteria from the project documents; absent documents = shipped-default behaviour, byte-compatible with today
- [ ] A project edit to a tagged criterion changes gate behaviour without code changes; an edit that removes a tag downgrades that criterion to human-judged visibly in gate output
- [ ] RFC0042's close-down enforcement is restated as the sprint-DoD close clause with no behavioural regression (existing close tests stay green)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
