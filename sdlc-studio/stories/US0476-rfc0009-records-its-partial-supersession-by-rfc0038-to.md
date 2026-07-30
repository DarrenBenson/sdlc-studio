# US0476: RFC0009 records its partial supersession by RFC0038, to the RFC0034 convention, element by element

> **Status:** Done
> **Delivers:** CR0434
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/rfcs/RFC0009-code-complexity-signals.md, sdlc-studio/rfcs/RFC0038-simplify-to-fibonacci-story-points-and-real-wsjf.md, sdlc-studio/rfcs/_index.md, tools/tests/test_supersession_records.py, CHANGELOG.md
> **Epic:** EP0172
> **Points:** 2

## User Story

**As an** agent reading an Accepted RFC to decide how a subsystem works
**I want** RFC0009 to carry the same partial-supersession record RFC0034 carries, on the file, the superseded rows, the index and RFC0038
**So that** the complexity-based estimation model that RFC0038 falsified at r=0.03 cannot keep reading as delivered live behaviour

## Acceptance Criteria

### AC1: all five elements CR0434 names are separately asserted

- **Given** RFC0009 after the edit, with status `Accepted (partially superseded)`, a `Partially superseded by:` header line linking RFC-0038, the RFC index Title-cell note (the shape RFC0034's row at rfcs/_index.md:53 already uses) and RFC0038's `Supersedes (in part):` header naming RFC-0009
- **When** each of the five is read from its own file by a separate assertion
- **Then** removing any single one turns the test red on its own line, so the status token and the index note are verified rather than only recited in a Given - the two elements the round-one AC set left unchecked
- **Verify:** pytest tools/tests/test_supersession_records.py::RFC0009RecordTests::test_each_of_the_five_supersession_elements_is_present
- **Verified:** yes (2026-07-30)

### AC2: every decision the header names as superseded carries the marker on its own row

- **Given** RFC0009's header naming its superseded decisions (D5) and workstreams (WS3), and the Open Decisions and Workstreams tables
- **When** the ids are parsed OUT of the header line and each named row is looked up in the tables
- **Then** each named row carries a `Superseded by RFC-0038` marker, and naming a sixth id in the header without marking its row turns the test red - the id list is derived from the prose, never hard-coded, so the check cannot pass by agreeing with itself
- **Verify:** pytest tools/tests/test_supersession_records.py::RFC0009RecordTests::test_every_header_named_decision_row_carries_the_superseded_marker
- **Verified:** yes (2026-07-30)

### AC3: the two files agree, read from both sides

- **Given** the ids RFC0009 declares as its superseder and the ids RFC0038 declares it supersedes in part
- **When** both declaration sets are read from source and compared
- **Then** they match, so a later one-sided edit to either file fails here rather than surviving as the exact asymmetry CR0434 was filed for
- **Verify:** pytest tools/tests/test_supersession_records.py::RFC0009RecordTests::test_rfc0009_and_rfc0038_declare_the_same_pairing
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
