# BG1749: BG0960 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0960.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T04:12:35Z

## Summary

BG0960 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the repaired `_breakdown_fix` docstring still misstates when the Verify repair prints, now in the other direction (sprint.py:5112-5114): it says "the Verify line for every unit with a criterion that has no verifier, whatever else it lacks", but the code appends `VERIFY_FIX` only for a unit whose `ac_why` is `no-verifier` (sprint.py:5123), and `conformance.unit_is_ungroomed` returns that only when no criterion carries a verifier (conformance.py:294-295). Executed through `sprint plan`: a bug lacking Affects, whose AC1 carries `- **Verify:** pytest src/a.py` and whose AC2 carries none, is refused as "lacks Affects" with the field block and no Verify repair, although it is an ungroomed unit with a criterion that has no verifier. The sentence wants "for every unit none of whose criteria carries a verifier (`ac_why` `no-verifier`), whatever else it lacks" [LC-018]; RULINGS: Round one's "the `_breakdown_fix` docstring misstates when the Verify repair prints" is MOVED. Its field-template half now matches the code: "the field template unless every unit's only miss is that verifier" is `if not all(verify_only)`. Its Verify half went from too narrow (only a unit whose only miss is the verifier) to too wide (any unit with one unverified criterion). The code, the tests and the changelog are unchanged since round one, where they held. AC1, AC2 and AC3 still pass by execution (verify\_ac run --dry-run, 3 of 3), and the four recorded author mutants replay killed. The round-one reviewer mutation pass over this code stands.

## Steps to Reproduce

1. Read the round 2 REJECT of BG0960 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0960 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the repaired `_breakdown_fix` docstring still misstates when the Verify repair prints, now in the other direction (sprint.py:5112-5114): it says "the Verify line for every unit with a criterion that has no verifier, whatever else it lacks", but the code appends `VERIFY_FIX` only for a unit whose `ac_why` is `no-verifier` (sprint.py:5123), and `conformance.unit_is_ungroomed` returns that only when no criterion carries a verifier (conformance.py:294-295). Executed through `sprint plan`: a bug lacking Affects, whose AC1 carries `- **Verify:** pytest src/a.py` and whose AC2 carries none, is refused as "lacks Affects" with the field block and no Verify repair, although it is an ungroomed unit with a criterion that has no verifier. The sentence wants "for every unit none of whose criteria carries a verifier (`ac_why` `no-verifier`), whatever else it lacks" [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG0960 AC1 still passes: Refusing a unit that already has Affects and Points but no verifier names a Verify line as the fix. Fails on: the refusal prints only the Affects and Points templates, so no Verify line is named as the fix.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BreakdownGateTests::test_the_refusal_names_the_unit_what_it_lacks_and_the_fix_for_a_missing_verifier
- [ ] **AC3** BG0960 AC2 still passes: A unit missing Affects or Points still gets today's field template, and a batch holding both kinds of miss shows both repairs, each once. Fails on: `_breakdown_fix` always formats the one `BREAKDOWN_FIX` block, so a batch with both kinds of miss shows one repair and not each once.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BreakdownGateTests::test_each_kind_of_miss_gets_its_own_repair
- [ ] **AC4** BG0960 AC3 still passes: `sprint.py breakdown`, which prints the same fix block, shows the same matched repair for a no-verifier unit. Fails on: `sprint.py breakdown` shares `_breakdown_fix` and prints the field templates for a no-verifier unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BreakdownGateTests::test_breakdown_prints_the_verify_repair_for_a_no_verifier_unit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
