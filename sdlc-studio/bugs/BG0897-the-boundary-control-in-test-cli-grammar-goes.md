# BG0897: The boundary control in test_cli_grammar goes red when the corpus holds no open cross-epic reference, so a seal blocks the push

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py
> **Evidence:** pre-push refusal of c70de024 (RUN-01M3VF2J seal); ac_scope check at be48f303 vs c70de024
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:42:27Z

## Summary

RealTreeMarkerTests' control copies the repository and asserts every listed verb names a real-tree id there. `ac_scope.py` check reports only references into OPEN epics: before RUN-01M3VF2J's seal it named US0004, US0223, US0239 and US0953 (EP0244, EP0269, EP0270 open); the seal derived those epics terminal, so it names nothing and `test_the_control_is_green_in_either_fragment_state` and `test_the_control_holds_with_no_fragment_directory` go red at the push boundary (c70de024). The control's evidence depends on the live corpus's open work, a window any close can shut.

## Steps to Reproduce

1. A corpus whose epics are all terminal or hold no cross-epic AC reference. 2. `SDLC_STUDIO_BOUNDARY_SUITE`=1 pytest tests/`test_cli_grammar.py`::RealTreeMarkerTests -> two red, verb '`ac_scope.py` check'.

## Proposed Fix

Seed the copy with what each listed verb needs to answer (for `ac_scope`, an open epic and a story whose AC names that epic's distinctive word) so the control never depends on the live corpus's open work.

## Acceptance Criteria

- [ ] **AC1** Given a copy of a corpus in which every epic is terminal, so `ac_scope.py` check names nothing on the live tree, when the boundary control runs over the copy in each fragment state, then it is green, because the copy is seeded with what each listed verb needs to answer. Fails on: the current control at c70de024, red on '`ac_scope.py` check'
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RealTreeMarkerTests::test_the_seed_gives_every_open_work_verb_an_answer_on_a_closed_corpus
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
| 2026-10-02 | engineering seat (orchestrator) | AC1 Verify re-pointed at the per-commit seed test: the boundary control it named skips outside the push |
