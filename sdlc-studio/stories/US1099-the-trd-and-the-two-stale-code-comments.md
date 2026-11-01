# US1099: The TRD and the two stale code comments name sdlc_md.EXECUTES_VERIFIERS: stories and bugs execute their Verify lines, and CRs and RFCs refuse a command-shaped one

> **Status:** Done
> **Delivers:** CR0645
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, tools/tests/test_lean_trd_refresh.py, changelog.d/US1099.md
> **Epic:** EP0293
> **Points:** 3
> **Depends on:** US1098, US1080
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer releasing 6.2
**I want** the TRD and the two stale code comments to name `sdlc_md.EXECUTES_VERIFIERS` as the authority on which types execute their Verify lines
**So that** a rebuild from the TRD keeps the Verify lines the Fixed gate depends on (RV0028 TRD-1, Critical)

## Acceptance Criteria

- **AC1:** Given `sdlc_md.EXECUTES_VERIFIERS`, when the TRD is read, then it names that set as the authority, names every type in it as executing its Verify lines, and says a CR or RFC refuses a command-shaped Verify line
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdVerifierAuthorityTests::test_the_trd_names_the_executing_types
  - **Verified:** yes (2026-11-01)
- **AC2:** Given the comments in `file_finding.py` and `artifact.py` that CR0645 names, when they are read, then neither says only a story executes its verifier, and each names the set
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdVerifierAuthorityTests::test_the_code_comments_name_the_set
  - **Verified:** yes (2026-11-01)

## Notes

- Serves: Rowan Achterberg, End goal 3 (a release a consuming team can upgrade to, its documents true).
- Source: sdlc-studio/reviews/RV0028-unified-review-before-the-second-6-2-run.md, finding TRD-1, and CR0645's summary for the two comment locations.
- AC1 must fail on: a type added to `EXECUTES_VERIFIERS` that the TRD does not name, or the TRD still saying only a story executes. The type set is read from `sdlc_md`, never typed into the test (RETRO0135: compare structured content, not a prose phrase list).
- AC2 must fail on: either comment reverted to the story-only wording.
- Overlap: US1100 and US1101 edit trd.md and the same test module; deliver the three in sequence. Covers CR0645 AC1.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-31 | Claude Opus 5.5 | Groomed for run four (D0392): criteria with Verify lines, each criterion's mutant, overlaps and sequence |
| 2026-10-31 | Claude Opus 5.5 | Run-four plan (D0392): depends on US1080, which shares a file this unit declares |
