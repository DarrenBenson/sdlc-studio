# BG1530: ADR-012 says persona learning approval, close listing and signature are unbuilt while they are Done and shipped

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py, changelog.d/BG1530.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md ADR-012 Status line (1228) and 'Built so far' paragraph (1260-1266), against the §6 Persona memory row (557)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:03Z

## Summary

ADR-012 in `sdlc-studio/trd.md` is headed Accepted, not yet built (line 1228), and its Built so far paragraph (lines 1260 to 1266) says approval, the close's listing and the signature are open stories of EP0287, so no learning is live yet. The stories for exactly those three things (US1066, US1067 and US1068) are Done, and the code ships them: `persona_memory.py` has an approve subcommand and `sprint.py` applies strikes at sign. Section 6 of the same TRD (line 557) describes the behaviour in the present tense as shipped. A reader rebuilding from the ADR gets the opposite picture from a reader of section 6. The existing pin in `tools/tests/test_lean_trd_refresh.py` only checks that paths named under Not yet built do not exist, so the stale sentence is unguarded.

## Steps to Reproduce

1. Read `sdlc-studio/trd.md` line 1228: the ADR-012 Status line ends 'not yet built'.
2. Read lines 1263 and 1264: 'Approval, the close's listing and the signature are open stories of EP0287, so no learning is live yet'.
3. Read the Status line of the story files for US1066, US1067 and US1068 under `sdlc-studio/stories/`: each reads Done.
4. Read line 557 of the same TRD: the Persona memory row describes approval, the close stamping each approved learning and the strike at sign as working behaviour.
5. Search `tools/tests/` for the phrases 'open stories' and 'no learning is live': nothing pins them.
6. Expected: the ADR and section 6 agree with the story statuses. Actual: the ADR contradicts both.

## Proposed Fix

Update ADR-012 in `sdlc-studio/trd.md`: change the Status line to say what is built and what remains, rewrite the Built so far paragraph to include approval (US1066), the close's listing (US1067) and the signed-close gate (US1068), keep under Not yet built only what is truly absent, and add a revision row. Extend the ADR-012 test in `tools/tests/test_lean_trd_refresh.py` so that any story id the ADR names as open is checked against that story's Status line, and the test fails when the ADR calls a Done story open.

## Acceptance Criteria

- [ ] **AC1** Given ADR-012 in `sdlc-studio/trd.md`, when its Status line and Built so far paragraph are read, then they name approval (US1066), the close's listing (US1067) and the signed-close gate (US1068) as built, Not yet built holds only what is absent from the tree, and a revision row records the change. Fails on: a Status line ending not yet built, or the sentence saying no learning is live yet.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdAdr012Tests::test_adr_012_names_the_built_learning_stories_as_built
  - **Verified:** yes (2026-11-19)
- [ ] **AC2** Given an ADR text that calls a story open, when the ADR-012 check reads that story's Status line under `sdlc-studio/stories/`, then it fails for a story whose Status is Done and passes for one still open. Fails on: a check that stays green while the ADR calls a Done story open.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdAdr012Tests::test_a_done_story_called_open_fails_the_check
  - **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
