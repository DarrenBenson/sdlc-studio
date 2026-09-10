# BG0662: nothing checks a changelog fragment's SHAPE until the release cut, and 59 of 119 had drifted past it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .githooks/pre-commit, tools/tests/test_precommit_lane_order.py
> **Evidence:** 2026-09-10, this tree at f763a89a: `changelog.py compose` refused at BG0581.md; a sweep of changelog.d found 59 of 119 fragments whose first line was not the marker. After repair, compose reports `would compose 119 fragment(s) into Added, Changed, Fixed`.
> **Created:** 2026-09-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`changelog.py compose` requires every fragment's first line to be `<!-- section: <name> -->`, and refuses the WHOLE run on the first one that is not - correctly, because folding is destructive and a partial compose is worse than none. Nothing checks that shape when the fragment is WRITTEN. The pre-commit gate runs `changelog.py check`, which only lists uncomposed fragments and cannot see inside them, so a fragment in any other shape commits cleanly and sits there. Measured on this tree at the v5.1 cut: 59 of 119 fragments were unparseable - 27 headed `### <ID>`, 26 a bare bullet with no marker at all, 5 headed `### Fixed`, one prose paragraph. Every one had passed the gate on the commit that wrote it. The first thing that would have discovered the drift is the release cut itself, which is the single moment where a refusal costs the most and where the tempting remedy is `--apply` with the bad ones deleted by hand.

## Steps to Reproduce

1. Write `changelog.d/BG9999.md` whose first line is `### Fixed` rather than the marker.
2. Commit it. Every lane passes - `changelog.py check` reports the fragment as pending and looks no further.
3. At the release cut run `changelog.py compose`. It refuses on that one file and folds nothing, however many other fragments are well formed.
4. On this tree before the repair: 59 of 119 refused, the oldest from BG0581.

## Proposed Fix

Give `changelog.py check` a shape pass - parse every pending fragment and name each one that cannot be composed, with the same message `compose` would give - and run it in the pre-commit gate. A fragment is written by the same commit as the code, so the shape is decidable at exactly the moment the author is still there to fix it. Cheap: it reads the first line of each pending fragment.

## Acceptance Criteria

- [ ] **AC1** Given a pending fragment whose first line is not `<!-- section: <name> -->`, when `changelog.py check` runs, then it NAMES that fragment and exits non-zero. The existing check lists pending fragments and never opens them, so every shape defect in this corpus passed it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::FragmentShapeCheckTests::test_a_fragment_with_no_marker_is_named_and_fails_the_check
- [ ] **AC2** Given a pending fragment that IS well formed, when `changelog.py check` runs, then it is not reported as malformed. The paired control: a check that refuses every fragment satisfies the row above and stops every commit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::FragmentShapeCheckTests::test_a_well_formed_fragment_is_not_reported
- [ ] **AC3** Given a commit staging a malformed fragment, when the pre-commit gate runs, then the commit is REFUSED with the fragment named. A checker wired into nothing is the shape this repository has shipped before - the gate is the part a library test does not exercise
  - **Verify:** pytest tools/tests/test_precommit_lane_order.py::ChangelogShapeLaneTests::test_the_lane_refuses_a_staged_malformed_fragment

## Impact

A release cut is refused by the accumulated shape drift of dozens of past commits rather than by anything in the release, and the operator's fastest way out is to delete the fragments that refuse - which silently drops those units from the changelog.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-10 | Claude Opus 5 | Filed |
| 2026-09-10 | Claude Opus 5 | Ruled OPEN for v5.1 on 2026-09-10, under D0186's disclosure half. The 59 malformed fragments this bug was filed from were repaired by hand in the same session and `changelog.py compose` now reports 119 fragments folding cleanly, so the v5.1 cut is not blocked. What stays open is the GATE: nothing refuses the next malformed fragment at the commit that writes it, so the corpus will drift again between releases. That is a two-point guard on a run already past its appetite, and it is worth more filed with the measurement beside it - 59 of 119, oldest from BG0581 - than added to a batch closing today. |
