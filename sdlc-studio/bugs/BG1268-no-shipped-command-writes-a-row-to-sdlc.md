# BG1268: No shipped command writes a row to `sdlc-studio/lessons.jsonl`, the store the lane brief reads, and its build digest is full at five, so the next build lesson drops one US1132's AC3 needs

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** the orchestrator's friction log (R8-F9, R8-F10), and run eight (RUN-01M6RZQZ) US1132 review round 1 ([pre-existing])
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:27Z

## Summary

The lane brief carries lessons from `sdlc-studio/lessons.jsonl` alone, through `lessons.phase_digest`, capped at `INJECT_MAX = 5` per phase (`.claude/skills/sdlc-studio/scripts/lessons.py:1893`, `:1999-2009`). No command writes a store row: `lessons.py add` appends a markdown registry entry (or promotes one with `--global`) and `propose` offers a CR or a bug, so US1132's builder recorded LC-019 to LC-021 by calling `lessons.new_lesson` and `lessons.save_store` from a script. The build digest now holds 5 of 5 active lessons, so the next build-phase lesson pushes one of LC-019 to LC-021 out of the lane brief and turns US1132's AC3 red with no change to US1132's files. The groomer also aimed US1132's builder-traps criterion at the `lessons/` registry, which the brief never reads, so the criterion needed the store added to its `Affects` and its traps grouped to fit the cap.

## Steps to Reproduce

Run `lessons.py --help`: no subcommand writes `lessons.jsonl`. Add a sixth active build-phase row to the store the way US1132's builder did and render a lane brief: one of LC-019 to LC-021 is gone and the brief reports one dropped; US1132's AC3 verifier then fails.

## Proposed Fix

Add a `lessons.py` subcommand that validates and appends a class row to the store (class, rule, behaviour, phases, run, source) and refuses a duplicate class, and name it in `reference-scripts.md` and `help/lessons.md`; have a criterion that depends on a lesson reaching the brief assert against the digest's own selection, or let a lesson be pinned past the cap, so a newer lesson cannot turn an unrelated unit red; say in the groom guidance that builder traps meant for the brief belong in the store, not the `lessons/` registry.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The lane brief carries lessons from `sdlc-studio/lessons.jsonl` alone, through `lessons.phase_digest`, capped at `INJECT_MAX = 5` per phase...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `lessons.py --help`: no subcommand writes `lessons.jsonl`.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add a `lessons.py` subcommand that validates and appends a class row to the store (class, rule, behaviour, phases, run, source) and refuses a duplicate class...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
