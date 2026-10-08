# BG0997: A per-unit engagement-floor waiver pasted with the dashed v3 id does not waive the unit

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, changelog.d/BG0997.md
> **Evidence:** Field report, 2026-10-07, grooming Sprint 0 on sdlc-studio-lens (skill 6.1.0). Thirteen waivers were recorded as rule:engagement-floor:<display id>, the form the floor's own remedy prints, for ids such as BG-01KX8B04. engagement_floor.py check then reported waived 0 and all thirteen still violating. Rewriting the same subjects with the dash removed (rule:engagement-floor:BG01KX8B04) waived them.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Grok 4.7; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:14:33Z

## Summary

The floor looks a per-unit waiver up under the normalised id, and decisions.py waive stores the subject it was given. `norm_id` drops the dash a schema v3 id is spelled with, and `_norm_subject` only lowercases, so a waiver recorded as rule:engagement-floor:BG-01JQK3F8 is stored with the dash and looked up as rule:engagement-floor:BG01JQK3F8. The remedy text tells the operator to pass rule:engagement-floor:<id>, and <id> everywhere else is the display spelling, dash included. The waiver is accepted, written to the decisions log, and then exempts nothing. The floor stays red, which is how thirteen recorded waivers on a consuming project left the violation count unchanged.

## Steps to Reproduce

1. Write a multi-file Done unit whose id is BG-01JQK3F8 and which has no acceptance criterion. 2. Record a waiver with subject rule:engagement-floor:BG-01JQK3F8, the string the remedy prints when <id> is that unit. 3. Run `engagement_floor.py` check. The unit is still a violation and waived is false. 4. Record the same waiver as rule:engagement-floor:BG01JQK3F8. The unit is waived.

## Proposed Fix

Match a per-unit waiver on the normalised id of the subject tail, so the dashed display spelling and the dashless key are one waiver. Do that in the lookup, so a waiver already recorded with the dash starts to apply, and keep the dashless form working. Leave the stored decision text as the operator wrote it: a v3 dash is load-bearing in other remedies, and this one should not rewrite the log.

## Acceptance Criteria

- [ ] **AC1** A waiver recorded as rule:engagement-floor:BG-01JQK3F8 waives the unit BG-01JQK3F8 and no other unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::WaiverTests::test_per_unit_waiver_exempts_only_that_unit_for_a_dashed_v3_id
- [ ] **AC2** A waiver recorded with the dash already removed still waives that same unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::WaiverTests::test_per_unit_waiver_exempts_only_that_unit_for_a_dashed_v3_id_and_the_dashless_form

## Triage

- Reproduced at d02d28af through the shipped commands: `decisions.py waive --subject rule:engagement-floor:BG-01JQK3F8` records `D0001`, `decisions.waiver_for` finds it under the dashed subject, and `engagement_floor._unit_waiver(root, 'BG-01JQK3F8')` returns None, because it looks the waiver up under `sdlc_md.norm_id` (dashless) while `decisions._norm_subject` only lowercases. Pre-existing.
- Severity Medium stands: a recorded waiver exempts nothing and the floor stays red with no word why. Changelog fragment renamed to the unit-id convention (LL0004).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Grok 4.7 | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: reproduced on current code; changelog fragment renamed to the unit id |
