# BG0295: changelog.py compose folds every pending fragment into [Unreleased] and deletes them, with no release gate or confirmation, so a mid-sprint compose prematurely consumes unrelated units' fragments

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py
> **Severity:** Medium
> **Points:** 2

## Summary

compose is the release-time action that folds changelog.d/ fragments into [Unreleased] and consumes (deletes) them. Run at any other time it silently does the same to EVERY pending fragment, not just the caller's - so a routine 'add my one fragment then compose' folds and deletes ~100 other units' fragments, rewriting [Unreleased] and losing the per-unit files the release cut was meant to compose.

## Steps to Reproduce

1. changelog.d/ holds many pending fragments (one per delivered unit awaiting the next release). 2. Add one new fragment. 3. Run changelog.py compose to fold it in. 4. Observe: it composes ALL fragments (observed 116) into [Unreleased] and deletes every fragment file, not only the new one.

## Proposed Fix

Gate compose behind an explicit release intent (a --release flag or a confirmation), or make it refuse when [Unreleased] would be rewritten outside a release cut, so a single-fragment add never consumes the whole pending set. The fragment convention is that fragments accumulate and are composed once, at the release; compose run outside that context should say so rather than act.

## Acceptance Criteria

### AC1: a bare compose consumes nothing

- **Given** pending fragments in `changelog.d/`
- **When** `compose` runs without an explicit apply intent
- **Then** it reports what it WOULD fold and touches nothing - CHANGELOG.md and every fragment survive, so a habitual compose cannot destroy the pending set
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::ComposeReleaseGateTests::test_a_bare_compose_consumes_nothing
- **Verified:** yes (2026-07-26)

### AC2: only --apply folds and consumes

- **Given** the same pending set
- **When** `compose --apply` runs
- **Then** it folds and deletes the fragments as the release cut, and a bare run beforehand left them intact - the destructive form is opt-in and distinct
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::ComposeReleaseGateTests::test_apply_is_required_to_fold_and_consume
- **Verified:** yes (2026-07-26)

### AC3: the CLI a habit reaches for is dry-run

- **Given** the `changelog compose` command with no flag
- **When** it runs
- **Then** it prints what it would compose and names `--apply`, consuming nothing - the footgun is disarmed at the surface an author actually types
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::ComposeReleaseGateTests::test_cli_defaults_to_dry_run
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-25 | sdlc-studio | Created via `new` (deterministic) |
