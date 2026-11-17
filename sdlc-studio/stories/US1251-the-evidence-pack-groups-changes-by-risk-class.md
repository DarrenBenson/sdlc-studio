# US1251: The evidence pack groups changes by risk class, high-risk first, each with its second seat verdict

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0704
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_risk_groups.py, changelog.d/US1251.md
> **Epic:** EP0345
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The evidence pack groups changes by risk class, high-risk first, each with its second seat verdict
**So that** CR0704 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Changes are grouped by risk class, high first

- **Given** signed reports whose delivered units carry `Risk-class` high, elevated and standard in their committed files, listed in the reports in another order
- **When** `release_cut.py evidence-pack --version X.Y.Z --reports ...` writes the pack
- **Then** the changes sit under one heading per class in the order high, elevated, standard, each unit under its own class and once only, and a class with no change has no heading. Fails on: report order kept, a unit listed under two classes, or a high-risk change below a standard one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_risk_groups.py::RiskGroupTests::test_changes_are_grouped_by_class_with_high_first

### AC2: Each high-risk change states its second seat's verdict

- **Given** a high-class unit whose committed ledger holds an independent verdict from each of two seats, and a standard unit reviewed by one
- **When** the pack is written
- **Then** the high-risk entry names the second seat, its verdict and its date on a line of its own, and the standard entry carries no such line. Fails on: the second seat's verdict folded into the general review line, or the first seat's verdict printed twice
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_risk_groups.py::RiskGroupTests::test_a_high_risk_change_states_its_second_seat_verdict

### AC3: A high-risk change with no second seat verdict says so

- **Given** a high-class unit whose committed ledger holds one independent seat's verdict, or a second verdict that `critic.independence` does not accept
- **When** the pack is written
- **Then** the entry states that no second seat verdict is recorded, and the pack is still written. Fails on: the line left out, so a change board reads a high-risk change as doubly reviewed when it was not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_risk_groups.py::RiskGroupTests::test_a_missing_second_seat_verdict_is_stated

### AC4: The class is read from the commit, and an unknown one is named

- **Given** a delivered unit whose committed file carries no `Risk-class`, and another whose class is edited in the working tree after the commit
- **When** the pack is written at that commit
- **Then** the first is listed under standard and named as carrying no recorded class, and the second is grouped by its committed class. Fails on: an unclassed unit dropped from the pack, or an uncommitted edit moving a change between groups
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_risk_groups.py::RiskGroupTests::test_an_unknown_class_reads_standard_and_the_commit_decides

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
