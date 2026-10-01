# US0784: The advisory `revert-check` gate lane is retired; the per-unit `verify_ac.py revert-check` stays

> **Status:** In Progress
> **Merged from:** US0785, US0786, US0787 (backlog sweep 2026-09-24, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Delivers:** CR0552
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/help/gate.md, .githooks/pre-push, tools/enable-hooks.sh, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_revert_lane_retired.py, changelog.d/US0784.md, tools/tests/test_pre_push_hook.py, tools/tests/test_lean_push.py
> **Epic:** EP0239
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the release gate to stop running the advisory `revert-check` lane over the whole batch
**So that** a tag costs minutes less, nothing rewrites my tracked files in place during a gate run, and one fewer accumulator is kept

## Summary

Reshaped by D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from "run the lane in an isolated worktree" (5 points) to a deletion (2 points). The lane is advisory, so it never blocks, and it reverts production files in the live tree, which is the defect CR0552 records. Retiring it removes the defect and the cost together. Deleted: `_revert_check`, `_record_revert_yield` and `_REVERT_YIELD_REL` in `gate.py`, the `registry["revert-check"]` binding at the release boundary, the lane's tests in `test_gate.py` (`RevertCheckReportingTests`, `RevertCheckLaneTests`, and the `revert-check` name in the scoped-check loop), and every lane mention in `help/gate.md`, `.githooks/pre-push` (header and the release cost note) and `tools/enable-hooks.sh`. The per-unit CLI `verify_ac.py revert-check --unit` stays: an author runs it deliberately on one unit. The gitignored `sdlc-studio/.local/revert-check-yield.json` loses its only writer; its last figure (71 runs, 730 examined, 18 would-refuse) is quoted here so the measurement is not lost.

## Premise at HEAD

Executed at `85042135`:

```text
$ python3 .claude/skills/sdlc-studio/scripts/gate.py --boundary release --only no-such-lane
  [FAIL] selection: unknown check name(s): no-such-lane - valid: batch-size, changelog-fragments, conformance, constitution, disclosure, doc-coverage, doc-freshness, doc-surface, duplicate-id, engagement-floor, full-suite, hook-enabled, index-derived, integrity, module-alone, provenance, reconcile, release-rehearsal, revert-check, validate, window
gate: FAIL
exit=1
$ cat sdlc-studio/.local/revert-check-yield.json
{ "runs": 71, "examined": 730, "would_refuse": 18 }
```

## Acceptance Criteria

- [ ] **AC1** Given this repository, when `gate.py --boundary release --only no-such-lane` runs, then the valid-lane list it prints does not name `revert-check`, and `verify_ac.py revert-check --help` still exits 0. Fails on: HEAD lists `revert-check` among the release lanes (gate.py:2115)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_revert_lane_retired.py::RevertLaneRetiredTests::test_the_release_boundary_registers_no_revert_check_lane
- [ ] **AC2** Given the shipped `gate.py`, `.githooks/pre-push`, `tools/enable-hooks.sh` and `help/gate.md`, when each is read, then none names the `revert-check` lane or `revert-check-yield.json`. Fails on: HEAD gate.py:792 (`_REVERT_YIELD_REL`) and pre-push:151 (the release cost note naming the lane)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_revert_lane_retired.py::RevertLaneRetiredTests::test_no_shipped_file_names_the_lane_or_its_yield_file

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | sdlc-studio | Retitled: was 'No tracked file in the live working tree changes at any point while the lane runs' |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
| 2026-10-01 | sprint planning | Goal review round 1 (engineering seat): Affects completed; the per-unit verify_ac revert-check name stays. |
