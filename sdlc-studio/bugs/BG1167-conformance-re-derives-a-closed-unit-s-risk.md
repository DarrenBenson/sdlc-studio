# BG1167: Conformance re-derives a closed unit's risk band from today's tree, so a later unit's edit to a shared file fails a light APPROVE that was right when given, and the census names the wrong remedy

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, changelog.d/BG1167.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** devserver1 push of 1fbb6a46: '[FAIL] conformance: 2 non-conformant unit(s)'. route.estimate for US1082 and US1103 gives difficulty_band medium with max_cognitive 28. critic-verdicts.md holds light APPROVEs by qa-seat-US1082-r1 (0a792a44f477) and qa-seat-US1103-r1 (34875a02186d).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T08:27:14Z

## Summary

Run four (2026-11-01). US1082 and US1103 were each briefed at the light tier `critic.tier_for` derived, approved light, verified and closed. US1104 then extended tools/tests/`test_lean_prd_refresh.py`, which both units declare. route.estimate now scores that file at `max_cognitive` 28, so both bands read medium and `tier_for` returns full. `conformance.tier_covers` re-derives the band on every check, so both units went non-conformant, and the push gate's conformance lane refused the push of 1fbb6a46. Two defects. (1) The depth a review owed is judged against the tree as it is now, not as it was when the unit was briefed and reviewed, so a closed unit's conformance changes with work it did not do. (2) `_done_stages` sets `critiqued_missing` to `HALF_VERDICT` ('independent APPROVE verdict') even when an independent APPROVE is on file and only its depth fails. That is the misdirection `HALF_TIER` exists to prevent, and `critiqued_unmet` already gets it right.

## Steps to Reproduce

1. Brief a unit whose band is light, record a light APPROVE, and close it.
2. In a later commit, grow a file in its Affects past route's cognitive threshold.
3. Run `conformance.py check`: the unit is non-conformant, and `critiqued_missing` reads 'independent APPROVE verdict'.

## Proposed Fix

Judge the depth against the band the tier was derived from at brief time. Record the band, or the commit the brief was cut at, with the verdict, and re-derive at that commit. Have `_done_stages` name `HALF_TIER` for an independent but shallow APPROVE, as `critiqued_unmet` does.

## Acceptance Criteria

- [ ] **AC1** A unit approved at the tier its band derived when it was briefed stays conformant after a later commit raises the band of a file it declares.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
- [ ] **AC2** A conformance check of an independent APPROVE that fails only on depth names 'a review at the depth this unit's risk band demands', not 'independent APPROVE verdict'.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py

## Impact

A closed unit's conformance changes when a later unit touches a shared file. The push gate then refuses, and the only exit is a second, full-depth review of work already approved. The census also sends the reviewer looking for a verdict that is already on file.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
