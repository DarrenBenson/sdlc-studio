# US0864: a derived verdict that contradicts the author's note is filed as a finding naming both, and the close is not refused

> **Status:** Superseded
> **Delivers:** RFC0060
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0258
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a derived verdict that contradicts the author's note is filed as a finding naming both, and the close is not refused
**So that** RFC0060 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1: a note contradicting the derived verdict is FILED as a finding naming both.**
  - **Given** a close whose derivation is `partial` and whose `--goal-verdict` override asserts `achieved`
  - **When** the close runs
  - **Then** a finding is filed carrying both verdicts, the override's justification, and the clause that disagrees - the comparison is between two recorded verdict values, never a reading of free text, because a keyword match on prose would pass its own mutants
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::VerdictContradictionTests::test_a_contradicting_note_files_a_finding_naming_both
- [ ] **AC2: the close is NOT refused by the contradiction.**
  - **Given** the same close
  - **When** it runs
  - **Then** it completes and files its report - D0231, because a stall in the middle is exactly what the dark factory removes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::VerdictContradictionTests::test_the_close_is_not_refused_by_a_contradiction
- [ ] **AC3: a note that AGREES with the derivation files nothing.**
  - **Given** a close whose override and derived verdict carry the same value, or a close passing no override at all
  - **When** it runs
  - **Then** no contradiction finding exists - the discriminating half, because a check that files on every close reports nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::VerdictContradictionTests::test_an_agreeing_note_files_nothing
- [ ] **AC4: the filed finding is reachable from the report of record.**
  - **Given** a run that filed one
  - **When** the report is derived
  - **Then** the finding's id appears in it - a contradiction recorded where the signer cannot see it has disclosed nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::VerdictContradictionReportTests::test_the_contradiction_reaches_the_report_of_record

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, compare the override to the derived verdict and log the difference without filing anything | a contradiction is filed |
| AC2 | in `sprint.py`, refuse the close when a contradiction is detected | the close is not refused |
| AC3 | in `sprint.py`, file the contradiction finding unconditionally at every close | an agreeing note files nothing |
| AC4 | in `sprint_report.py`, omit the contradiction finding from the report payload | the contradiction reaches the report |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
