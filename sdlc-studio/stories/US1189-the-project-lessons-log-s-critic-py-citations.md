# US1189: The project lessons log's critic.py citations are re-anchored to the current tree and the reason on L-0370 is corrected

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0657
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/retros/LESSONS.md, tools/tests/test_lessons_log_citations.py
> **Epic:** EP0324
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The project lessons log's critic.py citations are re-anchored to the current tree and the reason on L-0370 is corrected
**So that** CR0657 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Every critic.py citation in L-0001 to L-0270 names a symbol critic.py defines

- **Given** the Revalidated reasons of L-0001 to L-0270 in `sdlc-studio/retros/LESSONS.md`
- **When** each `critic.py:<line>` citation is read
- **Then** each has a backticked symbol beside it and `critic.py` defines that symbol. Fails on: a bare line number with nothing to re-anchor it by, or a citation naming a symbol since renamed or removed
- **Verify:** pytest tools/tests/test_lessons_log_citations.py::LessonsLogCitationTests::test_each_critic_citation_names_a_symbol_critic_defines

### AC2: Each of those citations points at its symbol in the tree the unit lands on

- **Given** the same citations and `critic.py` at the unit's own commit
- **When** `lessons.py revalidate --check-citations` (US1188) is run over the log, or each line is read by hand where that command has not landed
- **Then** none of the `critic.py` citations in L-0001 to L-0270 is reported: every one is within the window of the symbol it names. Fails on: citations still 16 lines short of their symbols

### AC3: L-0370's reason says the index lane reports and never blocks

- **Given** L-0370's Revalidated reason
- **When** it is read
- **Then** it says `gate.py` `_index_derived` reports an index that does not re-derive and never blocks, that only a crash of the lane blocks, and that the commit hook's `reconcile settle` regenerates the index; it no longer says the lane refuses. Fails on: the reason as written in ae604272, which claims a refusal the code does not make
- **Verify:** pytest tools/tests/test_lessons_log_citations.py::LessonsLogCitationTests::test_l0370_says_the_index_lane_reports_and_settle_regenerates

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
