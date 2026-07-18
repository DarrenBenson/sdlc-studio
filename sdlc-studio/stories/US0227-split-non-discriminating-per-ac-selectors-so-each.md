# US0227: split non-discriminating per-AC selectors so each AC fails on its own regression

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories/US0172-per-attempt-telemetry-records-carry-an-attempts-list.md, sdlc-studio/stories/US0173-true-cost-with-rework-unit-cost-sums-priced.md, sdlc-studio/stories/US0163-close-owed-detector-terminal-delivery-units-since-the.md, .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Epic:** EP0075
> **Points:** 3

## User Story

**As an** engineer reading a story's Verified stamps
**I want** each AC to fail on a regression in its own behaviour
**So that** a green per-AC tells me which criterion holds, not merely that some test ran

## Acceptance Criteria

### AC1: US0172 and US0173 no longer share a selector

- **Given** both stories' ACs previously ran `-k AttemptsAndCost`, one selector covering the attempts list and the cost sum together
- **When** each AC's Verify line is read
- **Then** US0172 selects only the attempts-list cases and US0173 only the cost cases, so a regression in either is attributed to the story that owns it.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.DuplicateVerifierTests.test_the_named_stories_no_longer_share_a_selector
- **Verified:** yes (2026-07-18)

### AC2: US0163's two ACs are narrowed to their own behaviour

- **Given** AC1 and AC2 both ran the whole `test_close_owed.py` file, byte-identical
- **When** each is read
- **Then** AC1 selects the baseline and coverage decision and AC2 the unbaselined path, so neither AC is evidence for the other.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.DuplicateVerifierTests.test_us0163_acs_select_different_suites
- **Verified:** yes (2026-07-18)

### AC3: A duplicated Verify command is reported by the lint

- **Given** two ACs carrying a byte-identical Verify command
- **When** `verify_ac lint` runs
- **Then** the duplication is named with every AC that claims it, so this recurs visibly instead of silently - it is advisory, because two ACs asserting one indivisible behaviour is legitimate and the author decides.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.DuplicateVerifierTests.test_duplicates_are_reported_with_every_claiming_ac
- **Verified:** yes (2026-07-18)

### AC4: Whitespace and manual verifiers do not create false duplicates

- **Given** two ACs whose commands differ only in spacing, and several ACs marked `manual`
- **When** the lint runs
- **Then** the spacing-only pair IS reported as duplicates (the run is identical) while `manual` ACs are not, because nothing executes for them and there is no shared evidence to confuse.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.DuplicateVerifierTests.test_whitespace_normalised_and_manual_exempt
- **Verified:** yes (2026-07-18)

## Notes

The lint reports 17 duplicated selectors across this workspace at the time of writing. This
story fixes the four its `Affects` names; the remainder is pre-existing debt, now visible
rather than silent, and is not silently absorbed here.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored; the seeded AC3 (a lint for byte-identical Verify commands) kept and built here as the durable guard |
