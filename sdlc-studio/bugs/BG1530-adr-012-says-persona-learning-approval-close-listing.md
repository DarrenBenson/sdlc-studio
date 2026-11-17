# BG1530: ADR-012 says persona learning approval, close listing and signature are unbuilt while they are Done and shipped

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
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

- [ ] **AC1** The behaviour described is corrected: ADR-012 in `sdlc-studio/trd.md` is headed Accepted, not yet built (line 1228), and its Built so far paragraph (lines 1260 to 1266) says approval, the close's...
- [ ] **AC2** The proposed fix lands, pinned by a test: Update ADR-012 in `sdlc-studio/trd.md`: change the Status line to say what is built and what remains, rewrite the Built so far paragraph to include approval...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
