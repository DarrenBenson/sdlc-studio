# BG0459: A wholly unreplaced retro scaffold validates as filled-in: three demonstration rows carry no marker, the close discards the EXAMPLES report, and the verifier's `>= 6` threshold tolerates a lost marker

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/templates/reviews/retro.md, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Independent adversarial review of RUN-01KYTKA1 tranche D (engineering seat, isolated worktree, 28 mutation runs). US0555=REJECT, US0558=REJECT.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0558 exists so a retro created by the scaffold and left as its own demonstration cannot pass as a filled-in sprint record. Three separate holes let exactly that happen, and the third is why the first two were never caught.

The three demonstration rows in `## Actions raised` carry no `<!-- example -->` marker, so `demonstration_leftovers` cannot see them. A retro with every MARKED line replaced and that table untouched validates as `ok - 3 finding(s) all dispositioned (1 filed, 1 fixed in-sprint, 1 declined)`: a fabricated sprint record, complete with a bug id nobody filed, a `fixed-in` commit hash and a declined finding nobody raised, reported as a clean close. That falsifies the template's own "Replace every EXAMPLE row; a row left in place is reported at the close", the docstring's "the marker the shipped template puts on every worked example", and the test class's "every worked example carries a marker".

AC4's Given/When is "when THE CLOSE reads it", and the close does not report it. `_close_retro_validate` runs `retro.main validate` through `_run_cli`, which redirects stdout into a buffer and discards it on a zero exit, returning `f"{retro_id} valid"`. A real `close --dry-run` over this repository reported `ok retro-validate: RETRO0086 valid` for a freshly scaffolded, 100% unreplaced retro, with no EXAMPLES line anywhere.

AC4's verifier asserts `len(left) >= 6`, a threshold that tolerates a lost marker. Stripping `<!-- example -->` from one carried bullet SURVIVES all 215 tests of the module, so marker completeness is pinned by nothing and the unmarked Actions rows were undetectable by construction.

## Steps to Reproduce

```text
scaffold a retro, replace every MARKED line, leave `## Actions raised` untouched
  retro.main validate -> ok - 3 finding(s) all dispositioned
                         (1 filed, 1 fixed in-sprint, 1 declined)
  demonstration_leftovers -> []

sprint close --dry-run over this repo, RETRO0086 100% unreplaced
  -> ok retro-validate: RETRO0086 valid        (no EXAMPLES line)

mutant: strip `<!-- example -->` from one carried bullet
  -> SURVIVED all 215 tests of test_retro.py
```

## Proposed Fix

Mark the three `## Actions raised` demonstration rows, and pin marker completeness rather than a floor: assert the exact set of marked lines the shipped template carries, so a marker that goes missing reddens instead of being absorbed by a `>= 6`.

The close must surface the EXAMPLES report rather than discard it. `_run_cli` swallowing stdout on a zero exit is the general shape - a validator whose warning is only ever printed cannot reach an operator through a caller that captures and drops it.

## Acceptance Criteria

- [ ] Every demonstration row in the shipped retro template carries the `<!-- example -->` marker, asserted as an exact set rather than a floor, so a marker that goes missing reddens
- [ ] A retro whose every marked line is replaced but whose Actions-raised table is untouched is REPORTED as carrying demonstration leftovers, rather than validating as three dispositioned findings
- [ ] `sprint close` surfaces the retro validator's EXAMPLES report rather than discarding it on a zero exit, so an unreplaced scaffold is named to the operator at the close

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
| 2026-07-31 | Claude Opus 5 | AC1 and AC2 delivered ahead of the rest, because this sprint's own close writes a retro and the defect would have bitten it. The three `## Actions raised` demonstration rows now carry the marker, and the verifier asserts the worked-example count EXACTLY rather than as a `>= 6` floor - a floor cannot catch a marker going missing, which is why the unmarked rows survived. Both mutants confirm it: stripping the marker from an Actions row and from a carried bullet each redden the suite, where the second SURVIVED all 215 tests before. AC3 - the close discarding the validator's report on a zero exit - is NOT delivered and this bug stays open for it. |
