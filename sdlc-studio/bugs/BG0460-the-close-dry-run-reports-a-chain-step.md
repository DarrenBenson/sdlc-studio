# BG0460: The close dry-run reports a chain step as neither refusing nor unevaluated, and its 'all seven steps' claim stands against a ten-step chain

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional (4 criteria red-first. Two mutants applied singly, purged, restored byte-identical - `gate` dropped from the derived step set, and a skipped step reported as nothing at all: both KILLED. The derivation is asserted against `_CLOSE_CHAIN`, so a step nobody has written yet is covered too)
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Independent adversarial review of RUN-01KYTKA1 tranche D (engineering seat, isolated worktree). US0555=REJECT, with the report executed against this repository.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0555 promises `sprint close --dry-run` reports EVERY unmet prerequisite of every step of the close chain, and AC5 requires a step that was not evaluated to say so. `gate` is a `_CLOSE_CHAIN` step and appears in the report as neither `ok` nor `unevaluated` in any scenario.

Executed on this repository the report listed 11 lines with no `gate` among them and closed with "3 refusal(s), 0 step(s) UNEVALUATED", although `close_preflight` had returned before ever reaching its `gate.run_gate` call. A step that was not evaluated, reported as neither refusing nor unevaluated, is precisely what AC5 forbids - and the operator-facing help claims "EVERY refusal all seven steps would raise".

The countable claims around it are stale in two directions. "All seven close steps" appears in the code, the CLI help, the story title and the test, against a TEN-step `_CLOSE_CHAIN` previewed by NINE entries in `DRY_RUN_ACTION_STEPS`. "Three of the chain's steps exist to DO something" appears twice against five writers.

AC4's and AC5's verifiers never call `close_dry_run` at all. AC4's feeds `_dry_run_result` a two-element fabricated list, so the AC's second half - "the real close then does not refuse" - is verified nowhere in the suite; there is no test anywhere that follows a clean dry run with a real close. Mutating the unevaluated branch to note `"ok"` survives AC5's named selector and is killed only by an unnamed sibling.

## Steps to Reproduce

```text
sprint close --dry-run, executed against this repository:
  11 lines reported, no `gate` among them
  closes with: 3 refusal(s), 0 step(s) UNEVALUATED
  close_preflight returned before reaching its gate.run_gate call

_CLOSE_CHAIN            : 10 steps
DRY_RUN_ACTION_STEPS    :  9 entries
claims in code and help : "all seven close steps"

mutant: unevaluated branch -> note("ok")
  -> SURVIVED AC5's named selector
  -> killed only by test_a_step_that_raises_in_the_copy_is_unevaluated_not_ok
```

## Proposed Fix

Emit a `note("gate", ...)` on both the evaluated and the not-reached paths, so the step is present in the report under every scenario. Derive the step count from `_CLOSE_CHAIN` rather than restating it in four places - a hand-written count in the help text is a claim nobody re-reads when the chain grows.

Point AC4's and AC5's verifiers at `close_dry_run` itself. A verifier that feeds a fabricated list to a formatting helper is testing the formatter, not the claim.

## Acceptance Criteria

- [x] The `gate` chain step appears in the dry-run report under every scenario: as `ok` when evaluated, and in the UNEVALUATED count when the preflight returns before reaching it
- [x] The step count in the report, the CLI help and the story is derived from `_CLOSE_CHAIN` rather than restated, so a step added to the chain cannot leave a stale count behind
- [x] AC4's and AC5's verifiers call `close_dry_run`, and one test follows a clean dry run with a real close that does not refuse

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
