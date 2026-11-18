# US1292: The report page and the evidence pack state that a delegated signature was delegated and name its decision

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0729
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py
> **Epic:** EP0366
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The report page and the evidence pack state that a delegated signature was delegated and name its decision
**So that** CR0729 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The report page names the decision behind a delegated signature

- **Given** a run sealed by a delegated signature that names an accepted decision (US1291's signature block)
- **When** its report page is written by the seal and then read by `sprint_report.py check`
- **Then** the page's signature block states that the signature was entered under delegation and names the authorising decision id, and the check reads the page VALID. Fails on: a bare signature row for a delegated signature, or a page the disclosure turns INVALIDATED
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DelegatedSignatureTests::test_the_report_page_names_the_decision_behind_a_delegated_signature
- **Verified:** yes (2026-11-18)

### AC2: The evidence pack discloses a delegated signature on each change it accounts for

- **Given** two committed signed reports, one signed under delegation and one signed by the operator
- **When** `evidence_pack.py` builds a pack over both
- **Then** each change from the delegated report says, on its Accountable line, that the signature was entered under delegation and names the decision, and each change from the other report says nothing of delegation. Fails on: a pack that names the principal of a delegated signature as though they signed in person
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::BuildPackTests::test_a_delegated_signature_is_disclosed_with_its_decision
- **Verified:** yes (2026-11-18)

### AC3: A report signed by the operator carries no delegation line

- **Given** a run sealed with no delegation option
- **When** its report page is written and checked
- **Then** the signature block holds no delegation statement and no decision id, and the page reads VALID. Fails on: a delegation line printed on every signature, or an empty decision cell where none applies
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DelegatedSignatureTests::test_an_undelegated_signature_carries_no_delegation_line
- **Verified:** yes (2026-11-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
