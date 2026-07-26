# BG0299: sprint plan crashes with TypeError on every invocation - test_strategy is passed batch records where it expects ids

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Provenance:** Hit in the homelab project trying to plan a bug-closing batch; reproduced on a bare status query
> **Raised-by:** Claude Code; human; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Severity:** High
> **Points:** 1

## Summary

`sprint plan` is completely broken in v5.0.0. Every invocation dies before printing a single line of the plan:

```text
TypeError: expected string or bytes-like object, got 'dict'
  sprint.py:6329 in test_strategy -> sdlc_md.find_by_id(Path(root), uid)
  sdlc_md.py:1174 in norm_id -> re.sub(r"[^A-Za-z0-9]", "", rec)
```

The cause is a type mismatch between producer and consumer. `cmd_plan` builds `data["batch"]` as a list of unit RECORDS (dicts with `id`, `priority`, ...) at sprint.py:2264 - and other consumers read them that way, e.g. sprint.py:2593 does `b['id']`. But `test_strategy(root, batch)` at sprint.py:6314 is annotated `batch: list[str]` and iterates `for uid in batch: sdlc_md.find_by_id(Path(root), uid)`, so it hands a dict to `norm_id`, which calls `re.sub` on it.

The broken call is the one at sprint.py:3807, inside `_print_test_strategy`, which passes `data.get("batch")` straight through. The other caller at sprint.py:3852 passes a plain `batch` and is presumably fine - which is likely why this survived: the crash is only on the path that reads the PLAN's batch, not the run-state's.

Scope: not specific to one project or one flag. It fires on `--worklist` and on a bare `--bugs Open`, and on both `--format text` and `--format json`, because `_print_test_strategy` runs at sprint.py:4912 before any plan output is emitted. Nothing is written, nothing is printed, and the exit code is 1. `sprint breakdown` on the same batch is unaffected and works normally.

## Steps to Reproduce

In any initialised project:

1. `python3 <skill>/scripts/sprint.py plan --bugs Open --order priority`
2. Observe the TypeError above and exit 1. No plan is printed.
3. Same with `--format json`, and same with a curated `--worklist`.
4. `sprint.py breakdown --worklist <file>` on the same units succeeds, confirming the batch itself is well-formed and groomed.

Observed against the installed skill and confirmed present in the source repo at the same line (v5.0.0).

## Proposed Fix

Pass ids, not records, at sprint.py:3807 - `test_strategy(root, [b["id"] for b in data.get("batch") or []])`. Prefer that over making `test_strategy` accept both shapes: the annotation `batch: list[str]` is the honest contract, and the second caller already honours it.

Worth doing alongside, since the type confusion is the root cause rather than the one line: `data["batch"]` is a list of dicts while the run-state's `batch` is read as ids in several places (sprint.py:3601, 3675, 4002, 4039). Those two shapes sharing a name is what let this through. Give them distinct names, or normalise at the boundary.

A regression test would have caught it: `sprint plan` on a fixture project asserting exit 0 and non-empty output. `scripts/tests/test_sprint.py` exists but appears to have no case that runs `cmd_plan` end to end.

## Resolution

Fixed the caller, keeping `test_strategy`'s honest `batch: list[str]` contract, per the proposed
fix. `_print_test_strategy` now projects the plan's unit records to ids at the boundary
(`[b["id"] if isinstance(b, dict) else b for b in data.get("batch") or []]`) before handing them
to `test_strategy`. The regression the bug names - a `cmd_plan` run against a fixture with a
`## Test Levels` TSD - is now covered; the earlier plan tests all passed because a TSD-less fixture
makes `test_strategy` early-return before it ever iterates the batch.

## Acceptance Criteria

### AC1: sprint plan does not crash on a batch when the TSD names test levels

- **Given** an initialised project with an Open bug and a `sdlc-studio/tsd.md` whose `## Test Levels`
  section names the file the bug affects
- **When** `sprint plan --bugs Open` runs, in both `--format text` and `--format json`
- **Then** it exits 0 and prints the plan, rather than dying with `TypeError: expected string or
  bytes-like object, got 'dict'` before any output
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CliTests::test_plan_does_not_crash_when_the_tsd_has_test_levels
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | Claude Code | Created via `new` (deterministic) |
| 2026-07-26 | Claude Code | Fixed - caller projects batch records to ids; regression test added |
