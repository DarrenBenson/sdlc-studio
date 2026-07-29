# BG0354: Three more places still enumerate the v2 four-digit id, so a v3 ULID unit silently escapes them

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .githooks/commit-msg
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

BG0318 closed this in conformance.py. The same hole survives in sprint.py's reachable_end_state (a fail-open, so a ULID unit is reported reachable when it is not) and in .githooks/commit-msg's paste-ready Refs hint, which prints a WRONG id for a ULID unit rather than none. Same LL0013 class, third and fourth instances.

## Steps to Reproduce

Measured against the current tree, not read. With sdlc-studio/.config.yaml containing 'review:\n two_role_after: US0100\n':

 sprint.reachable_end_state(root, [{"id": "US0101"}]) -> Review | derived from the cuto; Reproduced directly at the shell:

 $ printf 'US01010 US01011: batch\n' | grep -oE '(US|BG|CR)-?[0-9]{4}' | tr -d '-'
 US0101
 US0101

 $ printf 'US-01JQK3F8 BG-01JQK4Z2: batch\n' | grep -oE '(US|BG|CR)-?[0-9]{4}' |

## Proposed Fix

See the summary; each cited site names its own remedy.

## Acceptance Criteria

### AC1: a unit the cutoff cannot be compared against is reported as capped

- **Given** a v3 ULID unit and a numeric two-role cutoff
- **When** it is read
- **Then** it is reported as reaching Review, not Done - an unanswerable comparison must not be read as clearance, which is the fail-open this closed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UlidUnitsAreNotFailedOpenTests::test_a_ulid_unit_is_reported_as_capped_not_skipped
- **Verified:** yes (2026-07-29)

### AC2: a numbered unit below the cutoff still reaches Done

- **Given** a unit whose id number is below the cutoff
- **When** it is read
- **Then** it reaches Done, so the report discriminates rather than capping everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UlidUnitsAreNotFailedOpenTests::test_a_numbered_unit_below_the_cutoff_still_reaches_done
- **Verified:** yes (2026-07-29)

### AC3: the commit-msg id hint reads both id eras

- **Given** a subject naming a v3 ULID unit
- **When** it is read
- **Then** the paste-ready trailer names the id verbatim rather than a truncated four-digit prefix that resolves to a different, real artefact
- **Verify:** shell printf 'fix(BG-01JQK3F8): x and US0101\\n' | grep -oE '(EP|US|PL|BG|TS|WF|RFC|CR|IS)(-[0-9A-HJKMNP-TV-Z]{8,}|-?[0-9]{4,})' | grep -qx 'BG-01JQK3F8'
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
