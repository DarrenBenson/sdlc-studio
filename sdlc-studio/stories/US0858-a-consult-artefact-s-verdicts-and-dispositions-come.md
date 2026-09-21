# US0858: a consult artefact's verdicts and dispositions come from closed sets, and a FILE disposition names an id that resolves

> **Status:** Draft
> **Supersedes:** US0840
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/consult.py, .claude/skills/sdlc-studio/scripts/tests/test_consult.py
> **Epic:** EP0256
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** a reader of a stakeholder consult
**I want** every verdict and disposition to come from a closed set, with a FILE disposition naming an id that resolves
**So that** a consult can be judged rather than read - an open vocabulary means no two consults are comparable

## Acceptance Criteria

Carried VERBATIM from US0840 (criteria AC1, AC2), which was groomed and goal-reviewed before it was split. The words are unchanged so the scope is provably the same as the parent's; what changes is that they are now sized where estimation is reliable.

### AC1: every consulted persona carries a verdict from the closed set, and a missing one is named

- **Given** a fixture consult artefact naming three personas with verdicts Approve, Concerns and Reject, and a copy of it with one persona's verdict cell emptied
- **When** `consult.py parse <path> --format json` runs through `main` on each
- **Then** the first returns three rows, each naming the persona, the cast role and a verdict from exactly {Approve, Concerns, Reject}; the second exits 2 naming the persona whose cell is empty; and a third copy whose verdict cell reads `Approve with notes` also exits 2, naming the value it could not place in the set
- **Mutant:** read an unrecognised or empty verdict as Approve, or drop that persona's row - a consult that lost a persona then counts as a full panel, and US0842's yield counts a verdict it never received
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultParseTests::test_every_persona_row_carries_a_verdict_from_the_closed_set

### AC2: a disposition is one of the closed set, and a FILE disposition names an id that resolves

- **Given** a fixture artefact whose dispositions table holds one valid row per disposition - FOLD, FILE naming an id present in the tree, DECLINED with a reason, OPERATOR RULING OWED - plus three built to fail: an empty disposition cell, a cell reading `will consider`, and a FILE row naming an id that resolves nowhere
- **When** `consult.py parse` runs
- **Then** the four valid rows are returned with their disposition, each of the three is returned marked `unanswered` with the reason that made it so, and the count of unanswered rows is part of the result, because US0841 reports on it
- **Mutant:** accept any non-empty cell as a disposition - `will consider` then answers a Reject, and the unanswered list US0841 prints is permanently empty whatever the consult found
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultParseTests::test_a_disposition_is_one_of_the_closed_set_and_a_file_id_must_resolve

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | decomposition | Split from US0840 (8 points, at the ceiling where estimation reliability falls off) in RUN-01M306PY under D0222. Criteria carried verbatim rather than rewritten, so nothing is silently dropped or widened in the split. |
