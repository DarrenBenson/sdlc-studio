# US0841: an unanswered stakeholder Reject is reported at the close, holding nothing, and the operator rules it

> **Status:** Draft
> **Delivers:** RFC0058
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0256
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator ruling on what ships
**I want** an unanswered stakeholder Reject printed where I plan and again where I close, holding neither
**So that** I rule on it while acting is still cheap, and never meet it as a gate

## Acceptance Criteria

D4 settled the rule: a stakeholder Reject INFORMS, holds no gate, must be answered in writing, and
an unanswered one is reported at the close. The stakeholder consult's objection was the timing, not
the rule - an owed list read only at the close is read at the most expensive moment, in an epic
whose title says feedback should arrive while it is still cheap to act on. So one reader serves both
`plan` and `close`. Answered means a disposition from US0840's closed set and nothing else; for the
one disposition that defers to a person, `OPERATOR RULING OWED`, the answer is a ruling recorded in
the named retro. D3's artefact shape is open, so this story reads the artefact only through
US0840's parser and never by its own regex.

### AC1: the close reports every unanswered stakeholder Reject and still closes

- **Given** an open run whose batch holds a unit stamped as covered by a consult artefact carrying one Reject whose finding row reads `OPERATOR RULING OWED`, and a close that is otherwise green
- **When** `sprint.py close --retro RETRO#### ...` runs through `main`
- **Then** it exits 0 and the close completes; one line names the unit, the persona, the verdict and the artefact path; and `close_preflight` returns that row with `blocking` false, so it appears in no blocker list and no checklist item is outstanding because of it
- **Mutant:** make the row blocking - the persona gains the veto RFC0058's non-goals exclude, and a close is then held by a verdict D4 ruled advisory
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StakeholderRejectReportedTests::test_the_close_reports_an_unanswered_reject_and_still_closes

### AC2: answered is the disposition, never the presence of a dispositions table

- **Given** five fresh copies of AC1's run, whose single Reject finding carries in turn FOLD, FILE naming an id that resolves, DECLINED with a reason, `OPERATOR RULING OWED`, and an empty disposition cell
- **When** the close runs on each
- **Then** the first three report no unanswered line naming that finding, the last two do, and all five exit 0
- **Mutant:** read answered as "the artefact carries a dispositions table" - every consult carries one, so nothing is ever reported and the rule D4 settled has no reader at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StakeholderRejectReportedTests::test_a_disposition_answers_a_reject_and_an_empty_cell_does_not

### AC3: sprint plan prints the same list from the same reader, and its exit code is unchanged

- **Given** AC1's batch planned rather than closed, and a paired copy identical but for the consult artefact having no Reject in it
- **When** `sprint.py plan ...` runs on each
- **Then** the first prints the same line the close prints, built by the one function both callers read, and the second prints none; and the two runs' exit codes are equal, so the owed list changes what is printed and nothing else
- **Mutant:** compute the list at the close alone - the operator learns what the stakeholders rejected at the moment the run ends, in an epic that exists because feedback is cheapest early
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StakeholderRejectReportedTests::test_plan_prints_the_same_owed_list_and_its_exit_code_is_unchanged

### AC4: an OPERATOR RULING OWED finding is answered by a ruling, and a self-ruled row stays reported

- **Given** three copies of AC1's run: one whose RETRO#### `## Known issues carried` table names the consult finding, ruled `not-stop-ship` by the operator; one with the same row ruled by the authoring session; and one with no such row
- **When** the close runs on each
- **Then** the first prints no unanswered line for that finding; the second and third both print it, the second marked as a proposal rather than a ruling on `critic signoff`'s own principal predicate; and all three exit 0, the mark holding nothing
- **Mutant:** accept any non-empty `Ruled by` cell, which `retro.carried_issues` does today - the session that ran the consult then answers its own owed Reject, and the reporting line certifies the thing it could not check
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StakeholderRejectReportedTests::test_a_ruling_answers_it_and_a_self_ruled_row_stays_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
