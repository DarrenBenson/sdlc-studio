# BG1474: The close retires a build-injected lesson class as quiet, so every lane brief loses its builder traps and test_agent_definitions turns main red

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, sdlc-studio/lessons.jsonl, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/reference-retro.md, changelog.d/BG1474.md
> **Evidence:** Push boundary on devserver1 for 45b97375, 2026-11-15: 1 failed, 9055 passed; run thirteen's close output 'quiet for 5 runs, retired LC-019, LC-020, LC-021'.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T20:34:31Z

## Summary

Run thirteen's close (retro-extract, RUN-01M7EYR3) retired LC-019 (a push-gate guard the per-commit run skips), LC-020 (git and harness state a test leaks) and LC-021 (lane paperwork the landing refuses) as quiet for five runs. All three are injected at build, so the lane brief's 'Lessons for build' block no longer carries their rules. `test_agent_definitions.py`::SpawnSiteTests::`test_the_lane_brief_carries_the_builder_traps`, which reads the live store, failed at the push boundary for 45b97375 with all nine traps missing, and the push of run thirteen was refused. A build trap is quiet because it reaches every builder, so quietness is not evidence it is obsolete. The same run also repeated LC-019 (BG1468, two boundary reds the lanes' selections skipped) and LC-021 (markdownlint refusals at the land), but the close records hits only from cited REJECTs, so it read them as quiet.

## Steps to Reproduce

1. At 45b97375, run pytest .claude/skills/sdlc-studio/scripts/tests/`test_agent_definitions.py`::SpawnSiteTests::`test_the_lane_brief_carries_the_builder_traps.`
2. See nine builder traps missing.
3. Read sdlc-studio/lessons.jsonl: LC-019, LC-020 and LC-021 are state retired, `retired_run` RUN-01M7EYR3.

## Proposed Fix

A class injected at build leaves the briefs only by graduating (its CR shipped, making the trap mechanical), never by being quiet: quiet retirement skips it. Restore LC-019, LC-020 and LC-021 to active through the shipped path, with the reason recorded on each row.

## Acceptance Criteria

- [ ] **AC1** Given a lessons store holding an active class injected at build with no hit in the last `QUIET_RUNS` runs, when the close's quiet-retirement step runs, then that class stays active, while a quiet class injected only at plan or review still retires. Fails on: a build-injected class retired for being quiet.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
- [ ] **AC2** Given HEAD, when the lane brief's lessons block is built, then it carries every builder trap `test_agent_definitions` names, with LC-019, LC-020 and LC-021 active in sdlc-studio/lessons.jsonl. Fails on: any of the three left retired.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::SpawnSiteTests::test_the_lane_brief_carries_the_builder_traps

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
