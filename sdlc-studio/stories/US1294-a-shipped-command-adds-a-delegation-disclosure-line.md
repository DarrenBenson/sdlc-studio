# US1294: A shipped command adds a delegation disclosure line to a signed report, and the report check still reads it VALID

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0730
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py
> **Epic:** EP0367
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A shipped command adds a delegation disclosure line to a signed report, and the report check still reads it VALID
**So that** CR0730 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A shipped command adds the disclosure and the report still checks VALID

- **Given** a filed, signed report in a throwaway project that `sprint_report.py check` reads VALID, and a decisions log holding an accepted decision
- **When** the shipped `sprint_report.py` command that adds a delegation disclosure is run naming the report and that decision
- **Then** the page's signature block and the report's JSON record each carry a line saying the signature was entered under delegation and naming the decision, the fingerprint is unchanged, and `sprint_report.py check` still reads the report VALID. Fails on: a disclosure that can only be made by editing the sealed page by hand, or one that turns the report INVALIDATED
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_delegation_disclosure_leaves_the_signed_report_valid

### AC2: A disclosure is refused for an unsigned report or an unaccepted decision

- **Given** an unsigned report, and a signed report beside a decisions log in which the named decision is absent or superseded
- **When** the command is run on each
- **Then** each run exits non-zero naming why, and the page and its JSON record are byte-identical to what they were. Fails on: a disclosure written onto a page nobody signed, or one citing a decision the log does not show as accepted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_disclosure_is_refused_for_an_unsigned_report_or_an_unaccepted_decision

### AC3: Repeating a disclosure writes it once

- **Given** a signed report that already carries a disclosure naming a decision
- **When** the command is run again with the same decision
- **Then** the page carries one disclosure line, the second run changes no byte, and the report still reads VALID. Fails on: a second line for the same decision, or a re-run that moves the page
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_repeating_a_disclosure_writes_it_once

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
