# BG1010: sprint_report.py build --run resolves the named run and then builds the page from the default run

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_build_named_run.py, changelog.d/BG1010.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py
> **Evidence:** sprint_report.py `cmd_build` (6066; the call at 6075): `build_report(root, args.id or _retro_for_run(root, state))`, with no run_id; `build_report(..., run_id=None, ...)` at 4479-4480. Re-checked at HEAD 508e2408 on 2026-11-12.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T08:37:24Z

## Summary

`cmd_build` calls `_run_state_for(root, args.run)` only to decide whether `--write` is refused, then calls `build_report(root, args.id or _retro_for_run(root, state))` without `run_id=args.run`, though `build_report` takes one (`sprint_report.py`:4480). So `build --run RUN-x` previews the live or default run's page, not the named run's, and cannot build a named run's page in a fresh clone. Confirmed by the code path at 31f63fae and again at 508e2408 (2026-11-12); found by the G1/G2 panel review (D0355).

## Steps to Reproduce

In a clone holding two runs' committed records, `sprint_report.py build --id <retro> --run <the older run>` renders figures from the live run, not the named one.

## Proposed Fix

Pass `run_id=args.run` (and the resolved record) through to `build_report`, so the preview is the named run's page.

## Notes

- Re-groomed at HEAD 508e2408 (2026-11-12). Not fixed: `git log -S "build_report(root, args.id or _retro_for_run(root, state))"` names only f820b5b4 (2026-09-24), which wrote the call before this bug was filed.
- `run_id` changes more than which record is read. `_ci_runs` (sprint_report.py:3033) returns no CI runs for a named run whose record froze none (:3042-3043), where an unnamed live preview reads the forge (:3044). `build --run <the live run's id>` is how `test_lean_report.py` (:179 and :184, `lean_run` freezes no CI runs) and `test_sprint_report.py` (:3426, :3741, :3754) preview the live run, so pass `run_id` only when `_run_state_for` resolved a record other than the live one, or the live preview stops reading the forge.
- Passing `record=` as well makes `_run_state_for` answer the tracked path (:2924-2925), so every figure cites `sdlc-studio/reports/runs/<RUN-ID>.json`. That is US0997's change; keep this fix to `run_id` so the two do not collide.
- US1001's second criterion needs this fix.

## Acceptance Criteria

- [ ] **AC1** `sprint_report.py build --run RUN-x --id RETROxxxx` in a clean clone holding RUN-x's committed record renders RUN-x's figures, not another run's
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_build_named_run.py::BuildNamedRunTests::test_build_renders_the_named_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: line references moved to 6066/6075 and 4479-4480; Affects gains test_lean_report.py, which previews the live run with `build --run`; Notes added on `_ci_runs`'s named-run branch and the `record=` overlap with US0997 |
