# BG1565: The TRD stamped 6.4.0 still says persona-learning approval and signing are open stories and no learning is live

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py, changelog.d/BG1565.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, cross lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md ADR-012 'Built so far' paragraph, lines 1260-1264; against sdlc-studio/prd.md:334 and docs/release-notes-v6.4.0.md ('Each review seat has a record ...')
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:58Z

## Summary

ADR-012 in the TRD, in its Built so far paragraph at lines 1260 to 1264, says approval, the close's listing and the signature are open stories of EP0287, so no learning is live yet. That was true when the paragraph was written on 2026-11-15 and is false at the 6.4.0 version the TRD is stamped with. The four stories it refers to, US1065 to US1068, are Done; the PRD row for persona learnings is Complete and names them; the release notes describe the loop as shipped; and the commands exist in `persona_memory.py` and in the sign command of `sprint.py`. The story that refreshed the specs for 6.4 enumerated the records table, the state section and the data architecture, so this paragraph fell outside what its test pins. The TRD describes itself as a rebuild blueprint, so a reader is told the learning loop is unbuilt.

## Steps to Reproduce

1. Open sdlc-studio/trd.md at lines 1260 to 1264 and read the Built so far paragraph of ADR-012: it says approval, the close's listing and the signature are open stories and no learning is live yet.
2. Open the US1065, US1066, US1067 and US1068 files under sdlc-studio/stories/ and read each Status line: all four are Done.
3. Run `persona_memory.py` with --help: the verbs learn-brief, propose, approve-brief and approve are listed. Run sprint.py sign with --help: the --strike flag is listed.
4. Open sdlc-studio/prd.md at line 334: the Persona learnings row is Complete and names US1058, US1059 and US1065 to US1068.
5. Read the TRD revision history: the last row touching ADR-012 is dated 2026-11-15, and the 6.4 refresh row names section 6 only.

## Proposed Fix

Rewrite the Built so far paragraph of ADR-012 to state what 6.4.0 ships: a seat proposes a learning, another seat approves or rejects it, the close lists every learning about to go live, and a learning reaches a brief only once the run is signed, naming US1065 to US1068 beside US1058 and US1059. Keep the Not yet built line only for what is still absent, and add a revision row. Extend tools/tests/`test_lean_trd_refresh.py` so that a story the TRD calls open or not yet built fails the test when that story's file reads Done.

## Acceptance Criteria

- [ ] **AC1** Given the Built so far paragraph of ADR-012 in sdlc-studio/trd.md, when it is read, then it states what 6.4.0 ships (a seat proposes a learning, another seat approves or rejects it, the close lists every learning about to go live, and a learning reaches a brief only once the run is signed) and names US1065 to US1068 beside US1058 and US1059, with a revision row for the change. Fails on: the TRD saying approval and signing are open stories and no learning is live.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdBuiltStateTests::test_adr_012_states_the_learning_loop_as_shipped
- [ ] **AC2** Given every story id the TRD calls open or not yet built, when the test reads each story's Status line, then none reads Done. Fails on: a story the TRD calls open whose file reads Done.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdBuiltStateTests::test_no_story_called_open_reads_done
- [ ] **AC3** Given a fixture TRD passage calling one Done story open and one Draft story open, when the same check runs, then only the Done story is reported. Fails on: a check that reports every story id, or one that passes the stale claim.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdBuiltStateTests::test_a_done_story_called_open_is_reported_and_a_draft_one_passes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
