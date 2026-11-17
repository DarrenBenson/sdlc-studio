# US1293: The TRD records the deferred signature ruling as an ADR, the sprint pages describe it and RFC0060 D6 is closed

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0729
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, sdlc-studio/rfcs/RFC0060-the-dark-factory-a-sprint-that-decides-for.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, tools/tests/test_lean_trd_refresh.py
> **Epic:** EP0366
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The TRD records the deferred signature ruling as an ADR, the sprint pages describe it and RFC0060 D6 is closed
**So that** CR0729 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The TRD records the deferred signature ruling as an ADR

- **Given** `sdlc-studio/trd.md`
- **When** its Architecture Decision Records are read
- **Then** one ADR, numbered next after the last, has Status Accepted, cites D0503 and RFC0065, and states both halves of the ruling: a closed run waits for the operator's signature and the next run may open on top of it, and a delegated signature records its authorising decision and is disclosed in the signature block, the report and the evidence pack. Fails on: a TRD with no ADR citing D0503, or one that still says an unsigned run blocks the next
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdSignatureRulingTests::test_the_trd_records_the_deferred_signature_ruling_as_an_adr

### AC2: The sprint pages name the delegation option that sign accepts

- **Given** `reference-sprint.md` and `help/sprint.md`, and the `sign` parser US1291 ships
- **When** each page is read against that parser
- **Then** each page carries a runnable `sprint.py sign` invocation using the delegation option the parser defines, and says a run awaiting signature does not block the next. Fails on: a page that names an option the parser does not define, or that leaves delegation out
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdSignatureRulingTests::test_the_sprint_pages_name_the_delegation_option_sign_accepts

### AC3: RFC0060's open decision D6 is closed with a pointer to RFC0065

- **Given** RFC0060's Open Decisions table and the note above it
- **When** the D6 row is read
- **Then** its ruling cell no longer reads Open, it names RFC0065, its decision cell names D0503, and the note no longer says D6 remains open. Fails on: a D6 row that still reads Open, or one closed with no decision id
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdSignatureRulingTests::test_rfc0060_d6_is_closed_with_a_pointer_to_rfc0065

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
