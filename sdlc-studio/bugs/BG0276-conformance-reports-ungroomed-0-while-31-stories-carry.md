# BG0276: conformance reports ungroomed=0 while 31 stories carry the bare {{define}} scaffold: US0411's machine-visible ungroomed count recognises only the new marker, so every story minted before it is invisible to the very count meant to surface them

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py,.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Severity:** Medium
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |

## Detail

Found while sizing Sprint 2. Measured on the live workspace:

- `conformance check` summary: `ungroomed: 0`
- stories on disk carrying the bare `{{define}}` AC scaffold: **31**
- stories carrying `UNGROOMED_AC_TOKEN` (the marker US0411 introduced): **0**
- `sprint breakdown --stories Draft`: **45 of 49** ungroomed (lacking `Affects`)

US0411 shipped in RUN-01KY7W1F to make the ungroomed count machine-visible. It does that by
having `refine` write an explicit marker and having `conformance.story_is_ungroomed` count that
marker. Both halves are correct for stories minted AFTER the change. But the entire pre-existing
backlog carries the OLD `{{define}}` scaffold, so the count reports zero while 31 such stories
sit in the workspace - the number is confidently wrong in the safe direction, which is the
failure mode this project treats as worse than a loud one.

This is a gap in my own Sprint 1 delivery: the story was verified against newly-minted stories
only, so the test could not see the legacy shape. The closing review did not catch it either -
both were looking at the writer, not at the corpus.

## Impact

Anyone reading `conformance` to judge grooming debt is told there is none. It also silently
weakens any gate or report built on that count.

## Acceptance Criteria

- [ ] AC1: the ungroomed count recognises the legacy placeholder scaffold as well as the marker
- **Given** a workspace holding stories with the bare `{{define}}` AC scaffold and stories with the explicit marker
- **When** `conformance check` runs
- **Then** both shapes are counted as ungroomed, and the summary reports the true total
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::UngroomedMarkerTests

- [ ] AC2: the count is asserted against a corpus holding BOTH shapes, not the writer alone
- **Given** the test fixture
- **Then** it contains a legacy-scaffold story and a marker story with deliberately unequal counts, so a one-shape-only counter reads differently and fails
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::UngroomedMarkerTests
| 2026-07-24 | sdlc-studio | Fixed and mutation-proven - reported count now matches the 16 on disk |
| 2026-07-24 | sdlc-studio | Delivered in commit 6ae0c80e, whose subject names BG0276 only - a `git add -A` swept both units into one commit. Attribution recorded here rather than by rewriting pushed history (CR0416) |
