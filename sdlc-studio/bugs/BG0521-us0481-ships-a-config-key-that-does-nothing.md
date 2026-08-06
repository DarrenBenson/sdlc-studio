# BG0521: US0481 ships a config key that does nothing at plan time, and batch add writes the unit before it refuses it

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/help/sprint.md
> **Evidence:** Independently established by the QA and engineering review seats at the RUN-01KZ79C1 batch boundary, each by execution against isolated fixtures, and each reporting `affects_check_mode`'s single call site at sprint.py:7179 inside cmd_batch.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Three defects, found by both adversarial seats independently at the RUN-01KZ79C1 boundary.

1. `sprint.affects_check` is INERT for `sprint plan`. `affects_check_mode` has exactly one call site - `cmd_batch`. `cmd_plan` renders the pre-existing advisory and never consults it. Executed: a plan over an offending unit produces byte-identical output under `warn` and under `block`, exiting 0 in both, printing the literal `advisory - nothing is refused`. US0481 AC4's Given is the setting absent, warn and block; its When is a plan running under each. That behaviour does not exist.

2. `batch add` under `block` WRITES BEFORE IT REFUSES. `run_state.add_to_batch` runs, the unit is appended to `batch` and to `batch_changes`, the message says it was added, and only then does the mode check print a refusal and exit 2. So a unit the operator was told was refused is in the batch the done-gate reads. This is the same write-above-the-check shape as BG0507, which was fixed in this same batch.

3. The `--format json` path skips the check entirely: the refusal sits in the text-render `else` branch, so a JSON invocation adds the unit, exits 0, and reports no finding.

`help/sprint.md` documents the setting as deciding what a finding does, for both verbs. It decides nothing for `plan`, and only what is printed after the write for `batch add`.

## Steps to Reproduce

1. Fixture with a unit whose `Verify:` targets a file its `Affects` omits.
2. `sprint.py plan --bugs Open --write` with `sprint.affects_check` absent, then `warn`, then `block` - diff the three outputs. They are identical, all rc 0.
3. With `block` set and a run open: `sprint.py batch add BG0001` - rc 2 with a refusal printed, and the unit present in `run-state.json`'s `batch` and `batch_changes`.
4. The same `batch add --format json` - rc 0, unit added, no finding reported.

## Proposed Fix

Call the shared resolver from `cmd_plan` and honour the mode there, which is what AC4 describes. Move the `batch add` check ABOVE `run_state.add_to_batch` so a refused unit is never written - the ordering is the guard, exactly as BG0507 established. Hoist the check out of the text-render branch so the JSON path is covered. Then pin AC4 by RUNNING A PLAN under each of the three settings, not by asserting the getter returns a string: the shipped verifier does the latter and passes while the behaviour is absent.

## Acceptance Criteria

### AC1: `affects_check: block` REFUSES at plan time, and differs from `warn`

- **Given** a project setting `affects_check: block` and a batch with an undeclared-file finding
- **When** `sprint.py plan` runs
- **Then** it refuses, and its output DIFFERS from the same run under `warn` - today the two are byte-identical and both print `advisory - nothing is refused`, while `help/sprint.md:305` says the setting "decides what a finding does"
- **Mutant:** leave `cmd_plan` without the shared resolver - the config key decides nothing and the help page is false
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AffectsCheckModesTests::test_block_and_warn_differ_at_plan
- **Verified:** yes (2026-08-06)

### AC2: `batch add` refuses BEFORE it writes, not after

- **Given** the same finding under `block`
- **When** `sprint.py batch add` runs
- **Then** the unit is NOT in the batch afterwards - today it is written and then refused, so the operator is told "refused" about a unit the done-gate can now see
- **Mutant:** keep the write ahead of the check - the refusal is a message rather than a refusal, which is the shape of every gate that reports what it did not do
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AffectsCheckModesTests::test_batch_add_refuses_before_writing
- **Verified:** yes (2026-08-06)

### AC4: the positive control - `warn` still warns, and a clean batch still passes

- **Given** the shipped default `affects_check: warn`, and separately a finding-free batch under `block`
- **When** `sprint.py plan` and `sprint.py batch add` run
- **Then** both proceed and `batch add` still WRITES the unit. A seat found no positive control anywhere in this plan: a refusal wired unconditionally satisfies all three refusal rows above and blocks `sprint plan` in every consuming project
- **Mutant:** in sprint.py, replace the mode lookup with an unconditional refusal - the rows above stay green while the shipped default stops working
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AffectsCheckModesTests::test_warn_still_warns_and_a_clean_batch_passes
- **Verified:** yes (2026-08-06)

### AC3: `--format json` applies the same check as the text path

- **Given** the identical batch and mode
- **When** the command is run with `--format json`
- **Then** the same refusal happens - today the json path skips the check entirely, so a machine caller is held to a weaker rule than a human one
- **Mutant:** gate the check on the text renderer - the two output formats enforce different rules and only one of them is tested
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AffectsCheckModesTests::test_json_and_text_enforce_the_same_rule
- **Verified:** yes (2026-08-06)

## Impact

An operator who sets `block` believes ungroomed `Affects` declarations are being refused at plan time. Nothing is. Worse, the one place the setting is honoured leaves the unit in the batch after saying it refused it, so the done-gate reads a unit the operator believes was rejected.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in sprint.py, skip the shared affects resolver inside cmd_plan | `affects_check: block` REFUSES at plan time, and differs from `warn` |
| AC2 | in sprint.py, reorder the affects check below the batch write | `batch add` refuses BEFORE it writes, not after |
| AC4 | in sprint.py, replace the mode lookup with an unconditional refusal | the positive control - `warn` still warns, and a clean batch still passes |
| AC3 | in sprint.py, gate that check on the text renderer so json skips it | `--format json` applies the same check as the text path |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
| 2026-08-06 | sdlc-studio | Groomed for the v5 release sprint: tool-derived criteria replaced with decidable ones naming their mutants, authored in the shape verify_ac actually parses |
