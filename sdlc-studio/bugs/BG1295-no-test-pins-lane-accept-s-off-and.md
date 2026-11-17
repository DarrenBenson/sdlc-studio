# BG1295: No test pins `lane accept`'s `off` and unrecognised `review.author_self_check` branches, so asking for the self-check gap under `off`, or reading a mistyped mode as off, survives every lane accept test

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py
> **Evidence:** BG1290 round-2 review (qa-seat-BG1290-r1), surviving mutants at lanes.py:339-343
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T18:17:54Z

## Summary

From BG1290's round-2 review (qa-seat-BG1290-r1, non-blocking). Two branches of the self-check check `lane accept` gained have no test. The mutant that asks for the gap under `off` (lanes.py:343, `gap = critic.self_check_gap(root, unit)` taken out of its condition) survives all 9 lane accept tests; through the CLI it prints "WARNING US0101: ... (`review.author_self_check`: off ...", contradicting changelog.d/BG1290.md ("under `off` it does not ask") and the `_brief_of` docstring ("`off` asks nothing"). The mutant that reads an unrecognised mode as off (lanes.py:339-342) also survives: with the config set to `blok` after the landing it moves the unit to Done, where the shipped code exits 2 with "refused rather than read as off". Each survivor was re-run alone through `sprint.py lane accept`.

## Steps to Reproduce

Apply either mutant to lib/lanes.py and run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py -q`: all pass.

## Proposed Fix

Add two tests to `test_lane_accept.py`: under `off`, a stale self-check is neither refused nor warned about and nothing on stderr names it; under an unrecognised mode such as `blok`, `lane accept` exits 2, records nothing and says the mode is refused rather than read as off.

## Acceptance Criteria

- [ ] **AC1** Given a landed unit whose Affects changed after its self-check, under `review.author_self_check: off`, when `sprint lane accept` records an APPROVE, then it exits 0, the verdict is recorded and nothing on stderr names the self-check. Fails on: the self-check gap being asked for, and warned about, under `off`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_off_neither_refuses_nor_warns_about_a_stale_self_check
- [ ] **AC2** Given the same unit with the mode mistyped as `blok` after the landing, when `sprint lane accept` runs, then it exits 2, records no verdict, leaves the unit's status as it was and says the mode is refused rather than read as off. Fails on: an unrecognised mode read as `off`, moving the unit to Done.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_an_unrecognised_mode_is_refused_not_read_as_off

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
