# BG1558: TS0001 is recorded Complete while its own check reports 28 findings and nothing runs that check

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** sdlc-studio/test-specs/TS0001-ep0010-ac-coverage-token-economy-learning-loop.md, sdlc-studio/test-specs/_index.md, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, changelog.d/BG1558.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, tsd lens, survived 3 of 3 refute votes; observed at sdlc-studio/test-specs/_index.md Summary by Epic table (TS0001 row, Status Complete), Coverage Summary ("Automated 0 (0%)", "Pending 42"), and Next Steps ("the specs sit Ready"); TS0001 header Status: Complete
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:09Z

## Summary

The test-spec index and the TS0001 header both record the spec as Complete, yet every row the checker inspects in its matrix still reads Planned and the checker reports 28 findings against it. The index also contradicts itself: the row says Complete, the Coverage Summary says 0 automated and 42 pending, and the Next Steps prose says the specs sit Ready. Nothing catches this because the `ts-check` and `epic-ts` verbs of `verify_ac.py` are called from no hook lane, no `gate.py` lane, no workflow and no transition. A test spec's status is therefore asserted by hand and never checked, and the gate's reconcile lane covers the index for drift only, not for whether the matrix supports the status.

## Steps to Reproduce

1. From the repository root run `verify_ac.py` with the ts-check verb and --spec naming sdlc-studio/test-specs/TS0001-ep0010-ac-coverage-token-economy-learning-loop.md.
2. Observe that the output ends with a line saying status Planned is not passing for AC3 and a total of 28 findings.
3. Open that spec and read its header: the Status is Complete.
4. Open sdlc-studio/test-specs/_index.md: the TS0001 row reads 28 cases, 0 automated, Complete; the Coverage Summary reads Automated 0 and Pending 42; the Next Steps prose says the specs sit Ready.
5. Search .githooks, .github, package.json and the scripts gate.py, transition.py and sprint.py for ts-check and epic-ts: no invocation is found.

## Proposed Fix

Make the record true first: move TS0001 to the status its matrix supports with the shipped transition tooling, let reconcile re-derive the index row, and reword the Coverage Summary and Next Steps prose so the three statements agree. Then make the check run: add an advisory-first lane to `gate.py` that runs the `ts-check` logic over every spec whose status claims completion and reports a spec whose matrix has non-passing rows, and have the transition of a test spec to Complete refuse when `ts-check` reports findings. Pin both with tests in `test_gate.py`: a fixture spec marked Complete with a Planned row is reported, and a spec whose rows all pass is clean.

## Acceptance Criteria

- [ ] **AC1** Given a fixture test spec whose header reads Complete and whose AC Coverage Matrix holds a Planned row, when `gate.py` runs, then an advisory lane names the spec and the count of non-passing rows; a spec whose rows all pass, and a spec at Ready with Planned rows, are not reported. Fails on: a spec claiming completion over a matrix that does not support it passing the gate unreported.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestSpecStatusLaneTests::test_a_complete_spec_with_a_planned_row_is_reported
- [ ] **AC2** Given a fixture test spec whose matrix holds a Planned row, when `transition.py set` moves it to Complete, then the transition is refused naming the `ts-check` findings and the file is unchanged; the same transition on a spec whose rows all pass succeeds. Fails on: a test spec reaching Complete by assertion while `ts-check` reports findings.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestSpecCompleteGateTests::test_complete_is_refused_while_ts_check_reports_findings
- [ ] **AC3** Given the fixture spec marked Complete over a Planned row, when `gate.py` runs with the new lane at its shipped default, then the lane is listed among the gate's lanes, its finding is counted as advisory and the gate's exit code is unchanged by it. Fails on: the lane absent from the registry, or a first release of it turning every project's gate red.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestSpecStatusLaneTests::test_the_lane_is_registered_and_advisory
- [ ] **AC4** Given this repository after the fix, when the new lane runs over sdlc-studio/test-specs/, then it reports nothing: TS0001 holds the status its matrix supports, moved with the shipped transition tooling, and the index row, Coverage Summary and Next Steps prose agree with it. Fails on: TS0001 still recorded Complete over 28 findings, or the index contradicting itself.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
