# BG0386: caller-check --unit is single-valued, so a repeated flag silently checks only the last unit and reports a clean batch

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** critic.py:2231 add_argument("--unit", required=True) - no action=append; the caller-check parser is the same shape
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`caller-check` declares `--unit` with `add_argument("--unit", required=True)` and no `action="append"`, so `--unit US0542 --unit US0543` keeps only `US0543` and argparse says nothing. The command reports on ONE unit while the caller believes it reported on the batch, and a clean result reads as a clean batch.

This has already produced a false measurement in this repository. During RUN-01KYKVZM a caller-check invoked with repeated `--unit` flags returned one finding; that was recorded as `caller-unnamed 5 -> 0` in a retro and in two commit messages before the library call was checked and showed 17 of 23. The invocation was the defect, not the code under test.

## Steps to Reproduce

1. `python3 critic.py caller-check --unit US0542 --unit US0543 --root .`
2. One finding is printed, for US0543 only. US0542 also has a finding when checked alone.
3. `python3 critic.py caller-check --unit US0542 --root .` -> a finding. The batch form hid it.

## Proposed Fix

Accept the batch: `--unit` repeatable (`action='append'`), plus a `--units` comma-separated form and `--from-run` for the open batch, matching how `verify_ac` scopes. Print the unit COUNT checked alongside the findings, so a caller can see the scope the answer covers rather than infer it.

## Acceptance Criteria

### AC1: a repeated flag checks every named unit

- **Given** `caller-check --unit US0001 --unit US0002`, both of which have findings
- **When** it runs
- **Then** both units appear in the output, rather than the last one silently replacing the first
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerCheckBatchTests::test_a_repeated_unit_flag_checks_every_named_unit
- **Verified:** yes (2026-07-29)

### AC2: the command states the scope it answered over

- **Given** any invocation
- **When** it reports
- **Then** it names how many units it checked, so a clean result names the scope it is clean over rather than leaving the reader to infer it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerCheckBatchTests::test_the_command_states_how_many_units_it_checked
- **Verified:** yes (2026-07-29)

### AC3: a batch form takes the open run's units

- **Given** an open run with an approved batch
- **When** `caller-check --from-run` runs
- **Then** every unit of the batch is checked without being named by hand
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerCheckBatchTests::test_the_open_run_is_available_as_a_batch_form
- **Verified:** yes (2026-07-29)

### AC4: the spelling that already worked still works

- **Given** several ids after a single `--unit` flag, the form the bare `nargs="+"` supported
- **When** it runs
- **Then** every id is checked, so the repair does not trade one dropped spelling for another
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerCheckBatchTests::test_several_ids_after_one_flag_still_work
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
