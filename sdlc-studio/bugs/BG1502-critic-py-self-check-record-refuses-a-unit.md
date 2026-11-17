# BG1502: critic.py self-check record refuses a unit until it claims its changelog.d fragment, though the release cut has already merged that fragment into CHANGELOG.md

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, changelog.d/BG1502.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) BG1501/US1173 repair, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T07:18:00Z

## Summary

In run fifteen, the BG1501 and US1173 repair builder found that `critic.py self-check record` refused both units until each carried a claim on its changelog.d fragment, but `release_cut.py changelog-cut` had already folded both fragments into CHANGELOG.md's 6.4.0 section and removed them. The builder had to word a claim saying the fragment now lives in the 6.4.0 section. A unit repaired after the cut cannot satisfy the rule as written.

## Steps to Reproduce

1. Cut a release with `release_cut.py` changelog-cut.
2. Repair a unit whose fragment the cut consumed.
3. Run critic.py self-check record: it refuses for a missing fragment claim.

## Proposed Fix

When a unit's fragment is absent from changelog.d but its id appears in a released CHANGELOG section, accept a claim on that section (or require none), and say so in the refusal.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects declares a changelog.d fragment that a release cut has folded into a released CHANGELOG.md section naming the unit's id and then removed, when `critic.py self-check record` takes a hand-in with a claim on that released section and none on the fragment, then the record is accepted. Fails on: a unit repaired after the cut being refused for a fragment that no longer exists.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_a_fragment_the_cut_consumed_is_covered_by_a_claim_on_its_released_section
- [ ] **AC2** Given the same unit and a hand-in with no claim on either the fragment or the released section, when the record is refused, then the refusal says the fragment was folded into the released section and that a claim on that section satisfies the rule. Fails on: a refusal that still asks for a claim on a file that is gone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_the_refusal_names_the_released_section_when_the_fragment_was_consumed
- [ ] **AC3** Given a unit whose declared fragment is absent from changelog.d and whose id appears in no released CHANGELOG.md section, when `self-check record` runs without a fragment claim, then it is refused as it is today. Fails on: a missing fragment waved through because the file is absent.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_an_absent_fragment_no_release_holds_is_still_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
