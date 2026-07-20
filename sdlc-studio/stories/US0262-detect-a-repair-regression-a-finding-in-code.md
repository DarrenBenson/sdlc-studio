# US0262: Detect a repair regression: a finding in code the previous round's repair touched is reported distinctly from a fresh finding

> **Status:** Ready
> **Delivers:** CR0358
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Epic:** EP0085
> **Points:** 5

## User Story

**As an** operator watching a review loop iterate
**I want** a finding that lands in code the previous round's repair touched to be named a repair regression
**So that** I can tell "the review is finding real defects" from "the repair loop is manufacturing them", which is the signal that decides whether another round is worth buying

## Acceptance Criteria

### AC1: Each round records the file set its repair touched

- **Given** a review round whose REJECT is followed by repair commits
- **When** the round is closed out
- **Then** the run state records that round's repaired file set, so the next round has something to compare against
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_round_records_its_repaired_file_set
- **Verified:** yes (2026-07-20)

### AC2: A finding inside the previous round's repair surface is classified a repair regression

- **Given** round 1 repaired `critic.py`
- **When** round 2 returns a finding located in `critic.py`
- **Then** that finding is reported as a repair regression, naming the round whose repair touched it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_finding_in_prior_repair_surface_is_a_repair_regression
- **Verified:** yes (2026-07-20)

### AC3: A finding outside that surface is reported as fresh

- **Given** round 1 repaired `critic.py` only
- **When** round 2 returns a finding located in `sprint.py`
- **Then** it is reported as a fresh finding, not a repair regression
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_finding_outside_prior_repair_surface_is_fresh
- **Verified:** yes (2026-07-20)

### AC4: Round 1 can never produce a repair regression

- **Given** a run whose first review round is in progress, with no prior repair recorded
- **When** findings are classified
- **Then** every finding is fresh, and no repair regression is reported against an empty prior surface
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_first_round_findings_are_always_fresh
- **Verified:** yes (2026-07-20)

### AC5: Classification is by file AND the finding's located lines, not file alone

- **Given** round 1 repaired one function in a large file
- **When** round 2 returns a finding elsewhere in that same file, outside the repaired lines
- **Then** it is reported as fresh, not a repair regression - a file-level match alone would call almost everything a regression on this codebase, where single files carry thousands of lines
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_same_file_outside_repaired_lines_is_fresh
- **Verified:** yes (2026-07-20)

### AC6: An unlocatable finding is reported as unclassified, never defaulted to fresh

- **Given** a round-2 finding with no parseable file location
- **When** it is classified
- **Then** it is reported unclassified with its reason, and is not silently counted as fresh - a default that hides a regression is the failure this story exists to prevent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_unlocatable_finding_is_unclassified_not_fresh
- **Verified:** yes (2026-07-20)

## Notes

RUN-01KXVYGR is the reference case: rounds 2, 3 and 4 each had a MAJOR **created by** the
previous round's repair, all three inside the same 40-line function. AC5's line-level
granularity is what makes that case detectable without calling every same-file finding a
regression.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-20 | sdlc-studio | Groomed: user story and ACs authored; line-level granularity and the unclassified case added |
