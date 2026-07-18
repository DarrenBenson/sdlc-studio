# US0219: gate tracks the test-suite runtime and warns before a long run

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, tools/gate_timing.py
> **Epic:** EP0072
> **Depends on:** US0216
> **Points:** 3

## User Story

**As an** engineer committing through the pre-commit gate
**I want** the long unit run announced before it starts
**So that** I set a sufficient timeout instead of killing a commit that looked hung

## Acceptance Criteria

### AC1: Each run's wall-time is recorded to a bounded history

- **Given** the gate has run the unit suite
- **When** the duration is recorded
- **Then** it is appended to a per-suite history in `sdlc-studio/.local/gate-timings.json`, keeping only the most recent runs so the estimate tracks this machine rather than a long tail spanning hardware changes.
- **Verify:** shell python3 -m unittest discover -s tools/tests -p test_gate_timing.py -k RecordTests
- **Verified:** yes (2026-07-18)

### AC2: A long expected run is announced before it starts

- **Given** a recorded history whose median exceeds the warning threshold
- **When** the gate is about to run the suite
- **Then** it prints the expected duration and a timeout to allow, so the cost is known in advance rather than discovered as a hang.
- **Verify:** shell python3 -m unittest discover -s tools/tests -p test_gate_timing.py -k EstimateTests
- **Verified:** yes (2026-07-18)

### AC3: The estimate degrades to silence, never to a wrong number

- **Given** no history yet, or a corrupt/unreadable timings file
- **When** the estimate is requested
- **Then** nothing is printed and the exit status is success - an advisory measurement must never fail a commit or invent a figure.
- **Verify:** shell python3 -m unittest discover -s tools/tests -p test_gate_timing.py -k DegradeTests
- **Verified:** yes (2026-07-18)

### AC4: The median resists one pathological run

- **Given** a history containing one outlier far above the rest
- **When** the expected duration is computed
- **Then** it reflects the typical run, so a single cold-cache or loaded-machine run does not inflate every subsequent estimate.
- **Verify:** shell python3 -m unittest discover -s tools/tests -p test_gate_timing.py -k MedianTests
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Grooming: AC3 (skip the unit suite for test-irrelevant changes) moved to its owning story US0220; `Depends on: US0216` declared |
