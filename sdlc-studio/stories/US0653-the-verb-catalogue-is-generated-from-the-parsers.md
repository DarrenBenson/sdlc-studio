# US0653: The verb catalogue is generated from the parsers, never typed

> **Status:** Done
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_docgen.py
> **Epic:** EP0211
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The verb catalogue is generated from the parsers, never typed
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the catalogue is GENERATED, and typing into it is refused

- **Given** `reference-scripts-surface.md`, whose verb table sits between
  `<!-- BEGIN GENERATED -->` and `<!-- END GENERATED -->` markers
- **When** `docgen.py surface` runs
- **Then** it rewrites only what lies between those markers and leaves every byte outside them
  alone, and a MALFORMED pair is refused as loudly as an absent one: a `BEGIN` with no `END`, an
  `END` before its `BEGIN`, and two `BEGIN`s. Treating a missing `END` as end-of-file is exactly
  how a generator eats a paragraph somebody wrote, and it is the shape the prose invokes without
  the plan covering it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GenerationThroughTheCliTests::test_a_target_without_markers_is_refused_by_the_cli
- **Verified:** yes (2026-08-08)

### AC2: `--check` reports drift and exits 0

- **Given** a catalogue with one verb's description edited by hand, and a second fixture with
  none
- **When** `docgen.py surface --check` runs on each
- **Then** the first prints a non-zero drift count and the second prints zero, and BOTH exit 0.
  The malformed-marker refusals are asserted in the same class, because a `--check` that runs
  over a file it should have refused reports a drift count about a region it invented.
  Exit 0 is the criterion, not an oversight: the operator's decision is that these guards report
  and never block, so a lane that fails a commit on documentation drift is the thing being
  refused here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GeneratedRegionTests::test_a_malformed_marker_pair_is_refused
- **Verified:** yes (2026-08-08)

### AC3: the catalogue lists every verb the surface enumerates, and no other

- **Given** the surface library's enumeration
- **When** the catalogue is generated
- **Then** every enumerated verb appears exactly once and nothing appears that the enumeration
  did not produce. The enumerator is PATCHED to a fixed fake for this - three known verbs, one
  name repeated - and the page is compared against that literal list. Generating from the live
  enumeration and comparing against the live enumeration is two things agreeing: truncation
  dies, and any mutant inside the shared enumerator survives on both sides at once
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GeneratedRegionTests::test_the_catalogue_lists_exactly_what_the_surface_enumerates
- **Verified:** yes (2026-08-08)

### AC4: no row carries a flag, asserted structurally

- **Given** the enumerated surface, whose verbs carry 677 option strings between them
- **When** the catalogue is read
- **Then** no generated ROW contains any `option_string` the enumeration knows about - asserted
  against the enumerator's own flag set rather than against a list of strings in the test. A
  substring check for `--` cannot work here: the page's own pointer sentence has to name
  `--help`, so a naive check would exempt exactly the strings that sentence adds and then pass
  on prose the generator emits. The flag set is asserted NON-EMPTY first - the criterion states
  677 across the surface - because a row check against an empty set passes vacuously and would
  hold whatever the page contained. 677 rows would need a budget allowlist entry on the day the page
  was born, and a page nobody can afford to keep goes stale rather than helping
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GeneratedRegionTests::test_no_generated_row_carries_a_flag
- **Verified:** yes (2026-08-08)

### AC5: `--format json` exists and answers what the page does not

- **Given** the page's claim that `--help` and `docgen surface --format json` answer WHAT FLAGS
- **When** `docgen.py surface --format json` runs
- **Then** it emits the surface with each verb's flags, and exits 0. The page points at this, so
  it has to be there: a pointer to an entry point nobody built is a worse answer than no pointer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GeneratedRegionTests::test_format_json_emits_the_flags_the_page_omits
- **Verified:** yes (2026-08-08)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | write the whole target file rather than only the marked region | the catalogue is GENERATED |
| AC1 | generate into an unmarked file rather than refusing it | the catalogue is GENERATED |
| AC1 | treat a `BEGIN` with no `END` as running to end-of-file | the catalogue is GENERATED |
| AC1 | accept an `END` that precedes its `BEGIN`, writing between them | the catalogue is GENERATED |
| AC1 | accept two `BEGIN` markers, writing from the first to the last `END` | the catalogue is GENERATED |
| AC2 | exit non-zero when `--check` finds drift | `--check` reports drift and exits 0 |
| AC3 | emit only the verbs whose script name sorts first, truncating the list | the catalogue lists every verb |
| AC4 | render each verb's flags into the table beside it | no row carries a flag |
| AC5 | accept `--format json` and emit the same markdown the page carries | `--format json` exists |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-08 | sdlc-studio | Plan review round 1 REJECTed. AC4's two halves collided - the page must carry no flags while printing `--help` - so a no-flag check would exempt exactly the strings that sentence adds and pass on the generator's own prose; it asserts against the enumerator's flag set now, and the pointer's other half becomes AC5 so `--format json` is required to exist rather than merely named. AC3 compared a live enumeration against a live enumeration, which any mutant inside the shared enumerator survives; it patches a fake. AC1 gains the malformed-marker row, which is how a generator actually eats a paragraph |
| 2026-08-08 | sdlc-studio | Plan review round 2 APPROVEd, ruling all three round-1 findings CLOSED. Its major is folded in - the flag set is asserted non-empty, since a row check against an empty set passes vacuously - along with rows for the other two malformed marker shapes. The AC3 row that mutated the TEST rather than production is dropped: a mutant nobody can apply to the shipped code is not a mutant |
