# US0253: run the test-noise gate leg in CI and broaden the leak detector beyond one shape

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, sdlc-studio/tsd.md
> **Epic:** EP0082
> **Points:** 3

## User Story

**As a** maintainer reading a green test run
**I want** the silence standard held by CI, not only by an opt-in hook
**So that** a noisy-but-passing suite cannot merge and train readers to skim past ERROR

## Acceptance Criteria

### AC1: CI runs the noise leg unconditionally

- **Given** the noise check runs only from the pre-commit hook's path-conditional leg, on clones that enabled hooks
- **When** the Lint workflow runs on a push or pull request
- **Then** it invokes `tools/skill-tests.sh` as its own step, so a leaked diagnostic on a green suite fails the build
- **Verify:** grep "skill-tests.sh" .github/workflows/lint.yml
- **Verified:** yes (2026-07-19)

### AC2: The detector catches the common leak shapes

- **Given** the detector matches only a line beginning `ERROR` or `WARN` followed by a path
- **When** a passing run prints `ERROR: msg`, `WARNING: msg`, `script: ERROR` or a traceback line
- **Then** the noise leg exits non-zero and prints the offending lines, while an allowlisted intentional emission still passes
- **Verify:** shell python3 -m unittest discover -s tools/tests -k NoiseShapeDetectorTests
- **Verified:** yes (2026-07-19)

### AC3: tsd.md says where the gate actually runs

- **Given** tsd.md asserts a test-noise gate leg holds the silence standard without saying where it runs
- **When** the CI step is in place
- **Then** tsd.md names CI as the enforcement point and the hook as the local echo of it
- **Verify:** grep "test-noise.*runs in CI" sdlc-studio/tsd.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
