# BG1549: The public why page says a bug reaches Fixed only when its criteria pass, but the gate accepts a Verify line never run

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** docs/why-sdlc-studio.md, tools/tests/test_doc_claims.py, sdlc-studio/bugs/BG1039-us1004-s-one-list-test-no-longer-requires.md, docs/whitepaper.md, changelog.d/BG1549.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, cross lens, survived 3 of 3 refute votes; observed at docs/why-sdlc-studio.md line 285-287 ('A team grown from your project'), against .claude/skills/sdlc-studio/scripts/transition.py:1003-1011 and reference-bug.md:269
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:09Z

## Summary

docs/why-sdlc-studio.md lines 286 to 287 state that a story reaches Done, and a bug Fixed, only when its criteria pass. For a bug that is false. The Fixed gate in transition.py refuses only when no criterion is ticked and none carries a `Verify:` line, or when a recorded run is red; a `Verify:` line that was never run, or that names a test file which does not exist, lets Fixed through. reference-bug.md line 269 says so outright, and README.md and AGENTS.md word the rule accurately, so the public evaluation page is the outlier and contradicts both the reference and the code. The corpus holds a live instance: BG1039 stands at Fixed with both criteria unticked and `Verify:` lines naming tools/tests/`test_prereq_list_is_ci_list_strict.py`, a file that has never existed in the history.

## Steps to Reproduce

1. Read docs/why-sdlc-studio.md lines 285 to 287. It says a bug reaches Fixed only when its criteria pass.
2. In a throwaway fixture project, create an Open bug whose criteria are all unticked and whose Verify lines name a test file that does not exist.
3. Run transition.py set for that bug with the status Fixed and --root pointing at the fixture.
4. Observed: the bug moves from Open to Fixed and the index is synced. No criterion ran.
5. Positive control: strip the Verify lines from the same bug and repeat. The move is blocked with the message that every acceptance criterion is unticked and none carries a Verify line.
6. In this repository, read sdlc-studio/bugs/BG1039: Status Fixed, both criteria unticked, and the test file its Verify lines name is absent from the tree and from the history.

## Proposed Fix

Correct the sentence in docs/why-sdlc-studio.md to claim what the gate enforces: a story reaches Done only when its executable criteria have passed, and a bug is refused Fixed when nothing speaks for the fix or a recorded run of its criteria is red. Add an assertion to tools/tests/`test_doc_claims.py` that the page does not claim a bug's criteria must pass. Re-examine BG1039: either point its Verify lines at a test that exists and record a run, or reopen it. Whether the gate should also refuse a Verify line that was never run is a design choice already stated in reference-bug.md and is not part of this fix.

## Acceptance Criteria

- [ ] **AC1** Given docs/why-sdlc-studio.md, when its account of the closing gates is read, then it says a story reaches Done only when its executable criteria have passed and that a bug is refused Fixed when nothing speaks for the fix or a recorded run of its criteria is red, and it does not claim a bug's criteria must pass. Fails on: the sentence that a bug reaches Fixed only when its criteria pass surviving on the public page.
  - **Verify:** pytest tools/tests/test_doc_claims.py::FixedGateClaimTests::test_the_why_page_claims_only_what_the_fixed_gate_enforces
- [ ] **AC2** Given BG1039 after the fix, when its record is read, then its Verify lines name a test that exists and a run of them is recorded, or the bug is reopened with a Revision History row saying why. Fails on: BG1039 standing at Fixed on Verify lines naming `test_prereq_list_is_ci_list_strict.py`, a file that has never existed.
  - **Verify:** pytest tools/tests/test_doc_claims.py::FixedGateClaimTests::test_bg1039_names_tests_that_exist_and_records_their_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | AC2 given the Verify line the DOC builder wrote and ran green; it had none |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Affects widened to docs/whitepaper.md, whose sentence that sprint sign moves a bug to Fixed only if its criteria and recorded run speak for it is the same over-claim; found by the DOC2 builder |
