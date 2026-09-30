# BG0841: The review cap has no per-unit exception path, so an operator-granted extra round can only land by force

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap_exception.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-review.md, changelog.d/BG0841.md
> **Depends on:** BG0850
> **Evidence:** Sprint 6 RUN-01M3HR74, BG0818 round 3 (D0285, D0286), 2026-09-28
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T17:45:57Z

## Summary

BG0818's bounded round 3 was granted by the operator (D0285) and APPROVED by the reviewer who rejected it, yet critic.py record refuses any verdict past `review.max_rounds` ('record refused ... at the cap of 2') and transition refuses Fixed while the last recorded verdict is a REJECT. The only exit was transition --force, recorded in D0286, so the verdict ledger holds two REJECTs and no APPROVE for a unit that passed review. The cap is right as a default; it has no way to honour a recorded operator exception for one unit.

## Steps to Reproduce

Re-run at HEAD 46cb9acf on 2026-09-30 through `critic.py record` in a throwaway git tree holding BG0001 (In Progress) with no run open, so nothing carries it:

1. `critic.py record --unit BG0001 --verdict REJECT --reviewer rev-a` twice: both written (rounds 1 and 2); no bug is filed, since no open run holds the unit.
2. `critic.py record --unit BG0001 --verdict APPROVE --reviewer rev-a` exits 2: record refused for BG0001: "BG0001 has 2 review round(s) recorded, at the cap of 2 (`review.max_rounds`)". `critic.py record --help` offers no flag naming a decision.
3. The D0287 lane: `review.max_rounds: 3` added to `sdlc-studio/.config.yaml` for one call writes the APPROVE as round 3, the config is restored, and `transition.py set --id BG0001 --status Fixed` exits 0.

The premise holds only in part. There is no per-unit exception path, but "can only land by force" is refuted: D0287 landed BG0818's round-3 APPROVE through the config lane with no `--force`. BG0818 itself was a CARRIED unit, which BG0850 answers. What stays is an operator-granted round on a unit that was never carried, taken today by editing the project config for one call.

## Proposed Fix

`critic.py record --exception Dxxxx` admits one further delivery round for the named unit when Dxxxx is an accepted decision in `sdlc-studio/decisions.md` whose decision text names that unit, and writes the decision id on the row, so the ledger records why the round exists. Each decision grants one round; without one the cap refuses as today. The carried-unit discharge needs no exception (BG0850, which lands first because both change `round_refusal`).

## Acceptance Criteria

- [ ] **AC1** Given a unit with two REJECTs from rev-a recorded while no run was open (never carried) and an accepted decision D0001 whose decision text names the unit, when `critic.py record --verdict APPROVE --reviewer rev-a --exception D0001` runs, then it exits 0, the written row names D0001, and `transition.py set --status Fixed` exits 0 with no `--force`; the same call without `--exception` is still refused at the cap. Fails on: HEAD, where argparse rejects `--exception` and the cap refuses the APPROVE
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap_exception.py::ReviewCapExceptionTests::test_an_accepted_decision_naming_the_unit_grants_one_round
- [ ] **AC2** Given the same unit, when `--exception` names a decision whose text does not name the unit, a superseded decision, or D0001 again after its round is written, or when the APPROVE comes from rev-b, then `critic.py record` exits 2, names the reason and writes no row. Fails on: an implementation that checks only that the decision id exists in the log, which writes every one of those rows; and one that raises the unit's cap for good, which writes the second D0001 round
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap_exception.py::ReviewCapExceptionTests::test_an_exception_that_does_not_grant_this_round_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Groomed: premise re-run at HEAD - holds in part (no exception path) but 'only by force' is refuted by the D0287 config lane, and BG0818 was a carried unit that BG0850 answers; re-scoped to an operator-granted round on a never-carried unit, disjoint from BG0850; two executable criteria; Depends on BG0850 (both change `round_refusal`); Points 2 to 3 (flag, decision lookup, row marking); Affects swaps reference-sprint.md and test_critic.py for reference-review.md and reference-scripts-review.md. |
