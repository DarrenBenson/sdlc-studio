# BG0349: Four modules still carry the naive fence toggle the parser fix replaced

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, tools/check_links.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, tools/tests/test_check_links.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYHVWK closing review, independent reviewers); agent; skill v5.0.0

## Summary

The closing review replaced the fence walker in `verify_ac.py` and validate.py with one shared CommonMark tracker. The reviewer confirmed the naive toggle survives in lib/`sdlc_md.py` (lines 392 and 1603), `file_finding.py` (482), `persona_resolve.py` (192) and tools/`check_links.py` (191 and 294). Each treats any three-character run as a closer, so an inner fence inside a longer one releases the block early and content after it is read as document.

## Steps to Reproduce

1. Read each cited line. 2. Feed each a document with a four-backtick block containing an inner three-backtick opener, or a fence line carrying an info string. 3. Observe the block released early.

## Proposed Fix

Call the shared `sdlc_md.fence_step` from each, deleting the local rule. `sdlc_md.py`:392 is the widest and should go first: it governs table-row counting that reconcile consumes, which is the index-corruption class.

## Acceptance Criteria

### AC1: the table iterator never releases a block on an inner fence

- **Given** a document whose four-backtick block quotes a three-backtick block containing a table
- **When** `sdlc_md.iter_tables` walks it
- **Then** no row inside the block is yielded, so reconcile never tallies an illustration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::IterTablesFenceTests::test_inner_fence_inside_a_longer_block_is_not_a_closer
- **Verified:** yes (2026-07-28)

### AC2: a fence carrying an info string never closes a block

- **Given** a block whose next fence line carries an info string (CommonMark 4.5: a closer may be
  followed only by spaces)
- **When** the table iterator walks it
- **Then** the block stays open and the table beneath it is content, not structure
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::IterTablesFenceTests::test_a_fence_carrying_an_info_string_never_closes
- **Verified:** yes (2026-07-28)

### AC3: the persona registry reads no persona out of quoted illustration

- **Given** a persona index whose four-backtick block quotes a persona bullet
- **When** `sdlc_md.persona_registry` parses it
- **Then** only the real bullet is registered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::PersonaRegistryFenceTests::test_bullet_inside_a_longer_fenced_block_is_not_a_persona
- **Verified:** yes (2026-07-28)

### AC4: the shell-hazard scrubber drops the whole nested block

- **Given** a field value whose four-backtick block quotes a three-backtick block holding a command
- **When** `file_finding._strip_code_blocks` runs before the hazard fingerprints
- **Then** nothing inside the block survives to be scanned
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::StripCodeBlocksFenceTests::test_inner_fence_inside_a_longer_block_is_not_a_closer
- **Verified:** yes (2026-07-28)

### AC5: a seat card's quoted H1 is not the seat's name

- **Given** a seat card whose four-backtick block quotes an example H1 ahead of the real one
- **When** `persona_resolve.seat_name` reads it
- **Then** the real H1 names the seat
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py::SeatNameFenceTests::test_h1_quoted_inside_a_longer_fenced_block_is_not_the_seat_name
- **Verified:** yes (2026-07-28)

### AC6: the link guard does not cry wolf on a nested documented example

- **Given** an artefact whose four-backtick block quotes a deliberately broken link
- **When** `check_links.check_body_links` runs
- **Then** nothing is reported, while a live broken link after the closer still is
- **Verify:** pytest tools/tests/test_check_links.py::NestedFenceTests::test_a_live_link_after_the_matching_closer_is_still_reported
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (RUN-01KYHVWK closing review, independent reviewers) | Filed |
| 2026-07-28 | Claude Opus 5 (RUN-01KYJZGZ delivery) | Fixed: all five sites call `sdlc_md.fence_step`; ACs added with pytest verifiers |
