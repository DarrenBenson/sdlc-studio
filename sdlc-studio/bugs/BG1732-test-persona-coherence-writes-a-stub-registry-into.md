# BG1732: `test_persona_coherence` writes a stub registry into the real personas folder, so a parallel persona-card test reads it and the push gate goes red

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_persona_coherence.py, changelog.d/BG1732.md
> **Evidence:** pre-push gate on devserver1 judging 7a858b4b (boundary-suite-last.log): FAILED `test_own_persona_cards_pass_standard.py`::OwnPersonaCardsTests::`test_this_repositorys_cards_break_no_blocking_rule`, first list holding sdlc-studio/personas/.stub-registry.md
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T18:41:28Z

## Summary

tools/tests/`test_persona_coherence.py` (line 374) writes `sdlc-studio/personas/.stub-registry.md` into the repository's own tree, parses it and unlinks it. In the push gate's parallel full suite, `tools/tests/test_own_persona_cards_pass_standard.py::OwnPersonaCardsTests::test_this_repositorys_cards_break_no_blocking_rule` globs `sdlc-studio/personas/*.md` at the same moment, finds the stub, and fails its premise that the check reads exactly these cards. It refused the push of 7a858b4b on devserver1 (1 red of 10,128) though nothing in that push touched either test.

## Steps to Reproduce

Run the full suite in parallel (`tools/run-suite.sh all`, or the pre-push gate) until the two tests overlap; the persona-card test fails with 'premise: the check reads these cards and no others', its first list holding `sdlc-studio/personas/.stub-registry.md`.

## Proposed Fix

Write the stub registry into a temporary directory (`read_registry` takes a path), so no test writes under the repository's own sdlc-studio tree, and pin that the coherence test leaves the personas folder's listing unchanged.

## Acceptance Criteria

- [ ] **AC1** Given `tools/tests/test_persona_coherence.py`, when its registry-parser test runs, then it writes its stub registry under a temporary directory and nothing under the repository's `sdlc-studio/` tree, so the listing of `sdlc-studio/personas/` is the same before, during and after it. Fails on: `REPO / "sdlc-studio" / "personas" / ".stub-registry.md"` written and unlinked in place, which a parallel test globbing that folder reads.
  - **Verify:** shell ! grep -q 'personas" / ".stub-registry.md"' tools/tests/test_persona_coherence.py && python3 -m pytest -q tools/tests/test_persona_coherence.py
  - **Verified:** yes (2026-11-23)
- [ ] **AC2** Given the coherence test and `tools/tests/test_own_persona_cards_pass_standard.py`, when both run in one parallel session, then both pass. Fails on: the persona-card test's premise failing on a stub card another test left in the folder.
  - **Verify:** shell python3 -m pytest -q -n 4 tools/tests/test_persona_coherence.py tools/tests/test_own_persona_cards_pass_standard.py
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Groomed: two executable criteria (no write under the repository tree, both tests green in one parallel session) |
