# US0220: gate skips the unit suite for test-irrelevant changes, named not silent

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, tools/gate_timing.py
> **Epic:** EP0072
> **Depends on:** US0219
> **Points:** 3

## User Story

**As an** engineer committing a docs-only change
**I want** the unit suite skipped and the skip stated plainly
**So that** I do not pay 2.5 minutes for a change that cannot break a test, nor mistake a skip for a pass

## Acceptance Criteria

### AC1: A docs-only change skips the unit suite and says so

- **Given** a staged change touching only files that cannot alter a unit-test outcome (README, CHANGELOG, `reference-*.md`, `help/`)
- **When** the pre-commit gate runs
- **Then** the unit suites are skipped and the skip is printed with its reason, while style, links, budgets, markdown and the artefact gate still run - a guard that quietly does not run is indistinguishable from one that ran and passed.
- **Verify:** shell python3 -m unittest discover -s tools/tests -p test_precommit_selection.py -k SkipTests
- **Verified:** yes (2026-07-18)

### AC2: Any test-relevant change forces the full suite

- **Given** a staged change touching `scripts/`, `templates/`, or `tools/` - alone or mixed with docs
- **When** the pre-commit gate runs
- **Then** the unit suites run; the skip never applies to a change that could alter a test outcome.
- **Verify:** shell python3 -m unittest discover -s tools/tests -p test_precommit_selection.py -k RunTests
- **Verified:** yes (2026-07-18)

### AC3: The hook wires the timing measurement around the suite

- **Given** the pre-commit hook as shipped
- **When** its test-suite section is read
- **Then** it estimates before the run and records the elapsed time after each suite, so US0219's history is actually populated rather than defined but never called.
- **Verify:** shell python3 -m unittest discover -s tools/tests -p test_precommit_selection.py -k WiringTests
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: AC1/AC2 seeded from the criterion mis-filed on US0219; AC3 added for the timing wiring; `Depends on: US0219` declared |
