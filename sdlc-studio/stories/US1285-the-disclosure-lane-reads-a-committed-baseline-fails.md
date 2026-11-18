# US1285: The disclosure lane reads a committed baseline, fails on a new finding and prints one line when nothing is new

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0725
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/disclosure.py, package.json, tools/disclosure-baseline.txt, .claude/skills/sdlc-studio/scripts/tests/test_disclosure.py
> **Epic:** EP0363
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The disclosure lane reads a committed baseline, fails on a new finding and prints one line when nothing is new
**So that** CR0725 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A finding the baseline does not hold fails the lane and is the only one listed

- **Given** a fixture skill tree with two standing findings recorded by kind and name in a baseline file, and a third finding the baseline does not hold
- **When** `disclosure.py --root <fixture> --baseline <file>` runs
- **Then** it exits non-zero and lists the third finding by kind and name, and neither standing finding. Fails on: the lane as it stands, which exits 0 whatever it finds, or one that reprints every standing line so the new one is lost among them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_disclosure.py::BaselineTests::test_a_new_finding_fails_and_is_the_only_one_listed

### AC2: Findings equal to the baseline print one line and exit 0

- **Given** the same fixture with only its two standing findings, and a second run after one of them is fixed
- **When** `disclosure.py --root <fixture> --baseline <file>` runs each time
- **Then** the first run prints exactly one summary line and exits 0, and the second also exits 0, naming the baseline entry that no longer applies so it can be removed. Fails on: a finding that was fixed failing the lane, or the standing findings still printed one per line
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_disclosure.py::BaselineTests::test_findings_equal_to_the_baseline_print_one_line

### AC3: The committed baseline and the lint lane agree with this repository

- **Given** `tools/disclosure-baseline.txt` and the `lint:disclosure` script in `package.json`
- **When** the lane's own command is run against this repository
- **Then** the script passes the committed baseline to `disclosure.py`, the baseline holds every current finding by kind and name, and the run exits 0 with one summary line. Fails on: a lane still run without the baseline, or a baseline of bare counts under which one finding can be swapped for another unseen
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_disclosure.py::BaselineTests::test_the_lint_lane_reads_the_committed_baseline

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
