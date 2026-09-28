# BG0823: sprint close --dry-run reports no goal, no units and no start time for a run whose state holds all three, and previews writes as done

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_dry_run_state.py, changelog.d/BG0823.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** /tmp/evals-v6-main/09-lean-sprint.transcript.txt lines 1198-1235 vs 1237-1250; BG0799 builder note; BG0800 round review Low
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:24:06Z

## Summary

Eval 09 on v6-main: `close --dry-run` printed checklist rows `goal-judged: no goal to judge`, `review-attribution: no units`, `known-issues: the run record carries no start time`, and `handoff ... from the None verdict`, while the real `close` moments later scaffolded the retro titled with the goal and listed both batch units. The preview's steps run against a scratch copy and the scaffolded scratch retro carries no run id, so the checklist cannot tie the retro to the run. The same preview prints `close: derived EP-... terminal` from the reconcile step although it derived only on the copy (BG0799 builder), and with --file-and-close previews review-current as passing (BG0800 review).

## Steps to Reproduce

Open a two-unit run with a sprint goal, record APPROVEs, then `sprint.py close --dry-run`: the checklist says no goal, no units, no start time.

## Proposed Fix

Tie the preview's checklist to the open run (pass the run state to `sprint_report.checklist` or write the run id into the scratch retro, as the retro scaffold fix does), and prefix every action the preview performs on the copy `[copy]` so it never reads as done.

## Acceptance Criteria

- [ ] **AC1** Given an open run with a goal, a start time and two batch units, when `close --dry-run` runs, then its checklist names the goal and both units and dates the run. Fails on: HEAD's no goal / no units / no start time
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_dry_run_state.py::CloseDryRunStateTests::test_the_preview_reads_the_open_run
  - **Verified:** yes (2026-09-28)
- [ ] **AC2** Given the preview's reconcile step derives a parent on the copy, then its output line says it did so on the copy. Fails on: HEAD's bare `close: derived EP-... terminal`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_dry_run_state.py::CloseDryRunStateTests::test_copy_actions_are_labelled
  - **Verified:** yes (2026-09-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
