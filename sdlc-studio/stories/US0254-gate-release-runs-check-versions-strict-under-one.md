# US0254: gate --release runs check_versions --strict under one exit code; a CHANGELOG mismatch fails

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, sdlc-studio/tsd.md
> **Epic:** EP0082
> **Points:** 3

## User Story

**As an** operator cutting a release
**I want** the strict version check bound into the release gate's single exit code
**So that** a CHANGELOG mismatch cannot reach a tag because nobody remembered a flag

## Acceptance Criteria

### AC1: The release gate binds the strict version lane

- **Given** the strict version check is invoked by nothing executable, only by a prose checklist bullet
- **When** `gate.py --release` runs
- **Then** the strict version check is a bound blocking lane, listed in the gate's reported checks and folded into its one exit code; the plain gate leaves it advisory
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_gate.py -k ReleaseVersionStrictLaneTests
- **Verified:** yes (2026-07-19)

### AC2: A CHANGELOG disagreement fails the release gate

- **Given** a fixture whose topmost released CHANGELOG heading disagrees with the other version homes
- **When** `gate.py --release` runs over it
- **Then** the gate exits non-zero and names the disagreeing homes, and passes once they agree
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_gate.py -k ReleaseChangelogMismatchTests
- **Verified:** yes (2026-07-19)

### AC3: Docs match the mechanical reality

- **Given** tsd.md stage 4 and its gate table describe version consistency as a blocking release gate held by nothing
- **When** the lane is wired
- **Then** tsd.md names the strict check as run by the release gate, and the release-gate.md bullet reads as confirmation rather than the only enforcement
- **Verify:** grep "check_versions --strict" sdlc-studio/tsd.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
