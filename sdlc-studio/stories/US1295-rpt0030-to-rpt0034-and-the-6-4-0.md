# US1295: RPT0030 to RPT0034 and the 6.4.0 evidence pack name the decision behind each delegated signature

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0730
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/reports, docs/evidence.md, tools/tests/test_evidence_page_committed.py
> **Epic:** EP0367
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** RPT0030 to RPT0034 and the 6.4.0 evidence pack name the decision behind each delegated signature
**So that** CR0730 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each of RPT0030 to RPT0034 names the decision behind its signature and checks VALID

- **Given** the committed reports RPT0030 to RPT0034, each signed by the orchestrator in the operator's name, and the accepted decisions in `sdlc-studio/decisions.md` that authorised those signatures
- **When** each report is read and `sprint_report.py check` is run on it
- **Then** each page and its JSON record carry the disclosure line US1294's command writes, naming the accepted decision whose text authorises that run's delegated signature, and each report reads VALID. Fails on: one of the five without its line, a line naming a decision that does not cover that run, or a report the amendment left INVALIDATED
- **Verify:** pytest tools/tests/test_evidence_page_committed.py::CommittedEvidencePageTests::test_each_delegated_report_names_its_decision_and_checks_valid

### AC2: The 6.4.0 evidence pack and the evidence page say which signatures were delegated

- **Given** `sdlc-studio/reports/evidence-pack-6.4.0.md` and `docs/evidence.md` after the five reports are amended
- **When** each is read, and `sprint_report.py evidence --out docs/evidence.md --check` is run
- **Then** both name RPT0030 to RPT0034 as signed under delegation, each with its decision id, name no other report so, and the evidence page still matches what the command regenerates. Fails on: a pack or page that shows the five signatures as entered by the operator, or an evidence page edited by hand away from its generator
- **Verify:** pytest tools/tests/test_evidence_page_committed.py::CommittedEvidencePageTests::test_the_evidence_pack_and_page_name_the_delegated_signatures

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
