# BG1268: No shipped command writes a row to `sdlc-studio/lessons.jsonl`, the store the lane brief reads, and its build digest is full at five, so the next build lesson drops one US1132's AC3 needs

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons_class_add.py, changelog.d/BG1268.md
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

- [ ] **AC1** Given a project store `sdlc-studio/lessons.jsonl`, when `lessons.py class-add --class <name> --rule <text> --behaviour <text> --phase build [--phase review] --source <text>` runs, then one validated active row is appended with the next `LC-` code, the run id when a run is open, and the source; `lessons.py classes` lists it; and the lane brief's build digest can select it. Fails on: the row written to the `lessons/` registry instead of the store, a missing code, or a malformed row the digest skips.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_class_add.py::ClassAddTests::test_a_class_row_reaches_the_store_and_the_digest
- [ ] **AC2** Given a store that already holds a class of that name, or a `--phase` the digest does not know, when `class-add` runs, then it refuses with the reason, exits non-zero and leaves the store byte-identical; a positive control with a new class and a known phase succeeds. Fails on: a duplicate class appended, an unknown phase stored, or a partial write.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_class_add.py::ClassAddTests::test_a_duplicate_class_or_unknown_phase_is_refused
- [ ] **AC3** Given `help/lessons.md` and `reference-scripts.md`, when a reader looks for how to record a class outside a retro, then both name `class-add` beside `retro.py extract` (which records a `[new: class]` Try item at the close) and say the lane brief reads the store, not the `lessons/` registry. Fails on: either page silent on the store, or `class-add` documented with flags the parser does not take.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_class_add.py::ClassAddDocsTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-14 | Claude Opus 5.5 (run twelve grooming, D0474) | Re-scoped at grooming: `retro.py extract` already records a `[new: class]` Try item as a store row (retro.py `_extract_classes`), and the full suite passes with 15 active build-phase rows, so the cap-drop half no longer reproduces. What stays real is no direct command to add a class row outside a retro, which CR0693's escape loop needs. Criteria rewritten with Verify lines; Affects gains the new test and the fragment |
