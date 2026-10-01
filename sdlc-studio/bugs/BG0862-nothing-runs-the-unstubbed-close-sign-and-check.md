# BG0862: Nothing runs the unstubbed close, sign and check on one run holding a carry, a ruling and a forced override

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_run_end_to_end.py, changelog.d/BG0862.md
> **Depends on:** BG0859, BG0848, BG0851, BG0850, BG0826, BG0829, BG0849
> **Evidence:** RUN-01M3RPSK: RPT0012 re-closed after d05b882f moved seven approved bugs by hand; goal review round 1, 2026-09-30 (QA seat: every close test stubs the chain with `_green_steps`)
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T16:08:18Z

## Summary

Every close and sign test stubs the close chain (`test_lean_close._green_steps`) or the seal (`test_lean_sign._seal_stubbed`), so no test proves the path the operator runs: close, commit, sign, check on a run that holds the things the signed page must disclose. RUN-01M3RPSK needed a hand transition before the close, a re-close and an operator ruling recorded outside the tooling before RPT0012 could be signed VALID. The candidate sprint goal (Maya signs, without a re-close, a report that checks VALID and names every operator ruling and carry) has no test that could fail on it.

## Steps to Reproduce

Re-run at HEAD 46cb9acf on 2026-09-30: the lean close fixture with an approved story at Review and an approved bug at In Progress (spans opened in the run, ACs verified, a token meter that grows), closed with the REAL chain (`sprint.py close --retro RETRO0001`, no stubs): `REAL close rc 0`, every step run, gaps carried as known issues. `sprint.py sign --report RPT0001 --principal Darren` (real seal): `sign: 2 moved to their terminal status`. `sprint_report.py check --report RPT0001` exits 1: `INVALIDATED ... model_tokens[0]: signed 5000, now 8000; tokens_total ...; eu_minutes[0]: signed 0.0, now 0.1; eu_minutes[1] ...; eu_tokens[1]: signed 0, now 8000` (BG0848). The chain itself runs in the fixture in about 8 seconds, so an unstubbed test is affordable.

## Proposed Fix

One end-to-end test on the lean fixture, as a schema 3 (ULID) project, with the REAL close chain and the real seal. The run holds: a story at Review and a bug In Progress, both approved, with a base ref and commits naming them; a unit carried at the review cap by its reviewer's round-2 REJECT; a `sprint decision resolve`; a `transition.py set --force` on a unit dropped from the batch; and a lesson class with two repeats after its recording run, which the close graduates into a CR.

Before the close, the carried unit's rejecting reviewer records a discharge APPROVE (BG0850) and the unit is moved to Fixed with `transition.py set` and no `--force`. That is the carry's own gate: the unit left the batch when it was carried, and the seal moves batch units only, so nothing else would ever end it. No batch unit is moved by hand before the close.

Then: a bare `sprint.py close`, which scaffolds the retro with the run id and the Known issues carried table (BG0826) and files no report; fill the table with a ruling for the carry's bug (BG0829) and one for the graduated class by its LC code (BG0849); `sprint.py close --retro`; commit; `sprint.py sign`; `sprint_report.py check`. The test lands last, since each dependency makes one of its assertions pass.

## Acceptance Criteria

- [ ] **AC1** Given that run, when the bare `sprint.py close`, the table filled, `sprint.py close --retro`, a commit, `sprint.py sign` and `sprint_report.py check --report` run in turn, with no stubbed chain step or seal, then: the second close, the sign and the check exit 0; `check` prints VALID; exactly one sprint report exists under `sdlc-studio/reports/` across both closes (the bare close files none), and it is the report the sign sealed and the check read. Fails on: HEAD, whose check prints INVALIDATED on the unit and run token rows (BG0848); a test that stubs `_green_steps` or `_seal_units`, which never reaches the moves the sign makes; and a flow that files the report twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_run_end_to_end.py::SignedRunEndToEndTests::test_close_sign_check_is_valid_first_time
- [ ] **AC2** Given the same run, when the carried unit's rejecting reviewer records the discharge APPROVE and `transition.py set --status Fixed` runs with no `--force`, then the transition exits 0 and the unit carries no Forced-override field; and after the sign, every batch unit is terminal while no batch unit was transitioned by the test before the close. Fails on: HEAD, where `critic.py record` refuses the APPROVE at the cap and the transition names the unanswered REJECT (BG0850); and on a flow that reaches Fixed with `--force`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_run_end_to_end.py::SignedRunEndToEndTests::test_the_carried_unit_ends_through_its_own_gate
- [ ] **AC3** Given the same signed page, when it is read, then it names the carried unit with its bug and the retro's ruling on that bug; names the graduation CR with the ruling the retro gave its LC class, and no UNRULED row; reads 'the operator ruled 1 time(s)' for the one `sprint decision resolve`; and lists the dropped unit's Forced-override under Waivers in force. Fails on: HEAD, whose page reads no operator ruling, 'no gate stood down for this seal' (BG0851) and the graduation CR UNRULED (BG0849)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_run_end_to_end.py::SignedRunEndToEndTests::test_the_signed_page_names_every_ruling_carry_and_override

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Filed groomed for goal review round 1: premise run at HEAD with the unstubbed chain and seal (close rc 0, sign moves both units, check INVALIDATED); AC1 made self-contained and the scaffolding close excluded from 'exits 0' (it asks for the retro to be filled); Depends on the seven units whose fixes its assertions need. |
| 2026-09-30 | sprint planning | Goal review round 2, finalised by hand: the fixture is schema 3 and graduates a lesson ruled by its LC class, named on the signed page (AC3); exactly one report across both closes, the one signed and checked (AC1; a bare close files none, run at HEAD); the carried, dropped unit ends at Fixed through `transition.py set` with no --force after its rejecting reviewer's discharge, since the seal moves batch units only (AC2). Points 3 to 5: three criteria over a schema 3 fixture holding a carry, a discharge, a ruling, an override and a graduation. |
