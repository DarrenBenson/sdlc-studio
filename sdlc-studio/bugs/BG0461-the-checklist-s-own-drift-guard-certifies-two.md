# BG0461: The checklist's own drift guard certifies two rows unchecked: `cycle_drift`'s third bucket is non-empty on the shipped tree and asserted by nothing, planned POINTS are computed nowhere, and a waiver records no authoriser

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** Independent adversarial review of RUN-01KYTKA1 tranche G (engineering seat, isolated worktree, 31 mutants, 5 survived). US0569=REJECT, US0572=REJECT, US0574=REJECT.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0574 AC3 claims the stage set cannot drift from the cycle it covers. `cycle_drift()` returns three buckets and the AC's verifier asserts only two. The third is ALREADY non-empty on the shipped tree: `retro.py` builds its subparsers inline in `main()` rather than publishing a `build_parser()`, so `retro validate` cannot be checked and 2 of the 18 rows are unverifiable while the guard reports green. Adding `assertEqual(drift["unverifiable"], [])` to that test FAILS on the unmutated tree today. Two mutants renaming ceremony verbs survived the full 91-test suite and the AC's own selector in isolation.

The reverse check is partial in a second way: `uncovered` walks only `sprint` verbs, yet 6 of the 18 rows name verbs in `critic`, `retro`, `lessons` and `handoff`, so a ceremony added to any of those scripts is never caught - while the shipped reference states the two cannot part.

US0569 AC1 requires planned units AND POINTS beside the delivered figures. Planned points are computed nowhere in the file and appear nowhere on the page, so the points half of "commitment against actual can be read without arithmetic" is unreadable. Its verifier cannot fail for the defect its own comment names: deleting the `_planned_ids` reconstruction entirely SURVIVES, because the fixture uses exactly one drop plus one add, so the raw batch and the reconstructed plan are both 3.

US0572 AC3 requires a waiver be recorded with its reason AND AUTHORISER. `record_waiver` takes only subject and rationale, and the decision-log schema has no who column. Worse, the scope tail is never validated against the checklist ids, so a waiver naming an item that does not exist records cleanly and is read by nothing - verbatim the defect `decisions.py` documents as having already shipped once.

## Steps to Reproduce

```text
cycle_drift() on the shipped tree:
  unverifiable: ['retro: retro.py ships but publishes no build_parser(),
                 so `retro validate` cannot be checked'] x2

mutant: "critic sprint-review" -> "retro bogus-verb"   SURVIVED (91 tests + own selector)
mutant: "retro validate"       -> "retro deleted-verb" SURVIVED
inverted probe: assertEqual(drift["unverifiable"], []) RED on the unmutated tree

mutant: _planned_ids reduced to `return ids`            SURVIVED (whole suite, own class)
  fixture is 1 drop + 1 add, so raw batch == reconstructed plan == 3

record_waiver(root, "rule:sprint-checklist:not-a-real-item", ...)
  -> records cleanly as D0002, read by nothing
record_waiver(root, "rule:sprint-checklist", ...)
  -> records cleanly as D0003, `outstanding` still lists all 6 items
```

## Proposed Fix

Assert the `unverifiable` bucket empty, and give `retro.py` a `build_parser()` so `retro validate` is checkable - a bucket the guard fills and nobody reads is a guard reporting its own blindness into a void.

Walk every script the rows name, not only `sprint`.

Compute planned points, or drop the claim from AC1. Rebuild the reconstruction fixture so drops and adds do not cancel: 1 drop and 0 adds separates raw 2 from planned 3.

Validate a waiver's scope tail against the checklist ids, and record the authoriser - a waiver whose subject matches nothing is a waiver covering nothing, which is the exact failure the code comment beside it already describes.

## Acceptance Criteria

- [ ] `cycle_drift`'s unverifiable bucket is asserted empty by US0574 AC3's verifier, and `retro.py` publishes a `build_parser()` so `retro validate` is checkable
- [ ] The uncovered check walks every script the checklist rows name, not `sprint` alone, so a ceremony added to `critic`, `retro`, `lessons` or `handoff` is caught
- [ ] Planned POINTS are computed and rendered beside the delivered figures, and the reconstruction fixture uses a drop count and an add count that do not cancel
- [ ] A waiver naming a scope that matches no checklist id is REFUSED rather than recorded, and an accepted waiver records its authoriser

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
