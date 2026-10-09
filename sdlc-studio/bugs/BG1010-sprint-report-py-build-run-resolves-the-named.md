# BG1010: sprint_report.py build --run resolves the named run and then builds the page from the default run

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_build_named_run.py, changelog.d/BG1010.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** sprint_report.py `cmd_build` (~5603): `build_report(root, args.id or _retro_for_run(root, state))`, with no run_id; `build_report(..., run_id=None, ...)` at 4080.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T08:37:24Z

## Summary

`cmd_build` calls `_run_state_for(root, args.run)` only to decide whether `--write` is refused, then calls `build_report(root, args.id or _retro_for_run(root, state))` without `run_id=args.run`, though `build_report` takes one (`sprint_report.py`:4080). So `build --run RUN-x` previews the live or default run's page, not the named run's, and cannot build a named run's page in a fresh clone. Confirmed by the code path at 31f63fae; found by the G1/G2 panel review (D0355).

## Steps to Reproduce

In a clone holding two runs' committed records, `sprint_report.py build --id <retro> --run <the older run>` renders figures from the live run, not the named one.

## Proposed Fix

Pass `run_id=args.run` (and the resolved record) through to `build_report`, so the preview is the named run's page.

## Acceptance Criteria

- [ ] **AC1** `sprint_report.py build --run RUN-x --id RETROxxxx` in a clean clone holding RUN-x's committed record renders RUN-x's figures, not another run's
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_build_named_run.py::BuildNamedRunTests::test_build_renders_the_named_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
