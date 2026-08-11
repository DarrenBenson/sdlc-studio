# BG0542: sprint plan under affects_check: block prints REFUSED, exits 0, and writes the unit into the batch - worse than the honest advisory it replaced

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, independent delivery review of BG0521. `git log -S 'REFUSED under sprint.affects_check'` returns only the repair commit, so the false wording is this run's, not pre-existing.
> **Verification depth:** functional (unit: the command driven as a subprocess in every mode and state, asserting the EXIT CODE rather than the wording, which is what the previous repair changed; mutation: every planned mutant applied and killed)
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0521 was filed because `plan` under `block` was byte-identical to `warn`. Its repair made the message say REFUSED. It did not make the command refuse.

Probed through the shipped CLI on a throwaway fixture: `sprint plan --worklist ... --write` under `sprint.affects_check: block` prints `Affects contradicted by the unit's own content - REFUSED under sprint.affects_check: block:`, exits 0, and writes the offending unit into the batch.

That is worse than the state it replaced. At the run's base ref the same path said `advisory - nothing is refused`, which was true. The repair replaced a true statement with a false one, and the word REFUSED is precisely the refusal-that-is-a-message this bug was filed to remove.

## Steps to Reproduce

1. Set `sprint.affects_check: block` in a fixture project. 2. Give a unit an Affects its own content contradicts. 3. `sprint plan --worklist <unit> --write`. 4. The output says REFUSED, the exit code is 0, and the batch contains the unit.

## Proposed Fix

Return non-zero and write nothing on the block path, which is what the word means and what the criterion says. The four criterion-level mutants all die on a clean tree, so the unit's tests are sound - they simply never assert the exit code or the batch contents through the command, which is where the behaviour lives.

Also: the CHANGELOG claims all three call sites ask one reader, `_affects_blocking`. `cmd_batch` calls `affects_check_mode(root)` directly, so only two of the three do.

## Acceptance Criteria

> **Restated before the repair, 2026-08-11.** The filed pair were the tool-derived criteria that
> restate the summary, which states nothing a test can fail on. The bug's own Proposed Fix is
> precise and is preserved: return non-zero and write nothing on the block path, and assert the
> EXIT CODE and the ABSENCE OF A RUN rather than the wording - the previous repair changed the
> word to `REFUSED` and left the command untouched, which is the whole defect.

### AC1

- **Given** a project recording `sprint.affects_check: block` and a unit whose own Verify line
  targets a file its `Affects` does not declare
- **When** `sprint.py plan --write` is run AS A SUBPROCESS
- **Then** it exits NON-ZERO and NO run-state is written. The refusal happens where every other
  refusal happens - before the run is opened - rather than in a renderer that runs afterwards and
  decides nothing.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k block_refuses_with_a_non_zero_exit
- **Verified:** yes (2026-08-10)
- **Mutant:** in `sprint.py`, remove the affects-block refusal from the plan path, restoring a renderer that prints REFUSED while the command exits 0.

### AC2

- **Given** the SAME project and unit under `sprint.affects_check: warn`
- **When** the same command is run
- **Then** it exits ZERO and the run IS written. Without this the criterion above is satisfied by
  a plan that refuses every contradiction whatever the mode - which is BG0521's defect inverted,
  and the config key would decide nothing again.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k warn_still_advises_and_plans
- **Verified:** yes (2026-08-10)
- **Mutant:** in `sprint.py`, drop the mode read from the refusal condition so every contradiction refuses.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, remove the affects-block refusal from the plan path, leaving the renderer that prints REFUSED | |
| AC2 | in `sprint.py`, delete the mode read from the refusal condition so every contradiction refuses | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
