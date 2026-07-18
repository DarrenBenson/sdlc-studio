# US0226: rewrite US0166 AC3 as a two-file shell Verify with the missing shell prefix

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories/US0166-ship-a-stop-hook-installer-and-redefine-sprint.md
> **Epic:** EP0075
> **Depends on:** US0228
> **Points:** 2

## User Story

**As an** operator trusting a story's Done record
**I want** US0166 AC3 to check the claim it makes
**So that** a green on a shipped story is evidence and not an accident of argument parsing

## Acceptance Criteria

### AC1: AC3's verifier checks both files it names

- **Given** AC3 claims that `reference-retro.md` and `help/gate.md` both state the close clause
- **When** its Verify line runs
- **Then** both files are checked and the AC fails if either stops stating it, because a criterion that names two files and inspects one is only half a criterion.
- **Verify:** shell cd .claude/skills/sdlc-studio && grep -q 'never at .deployed' help/gate.md && grep -q 'never at .deployed' reference-retro.md
- **Verified:** yes (2026-07-18)

### AC2: Both files also carry the enforcement half of the claim

- **Given** the same AC also claims both state the `--require-close` / Stop-hook enforcement
- **When** the verifier runs
- **Then** that half is checked too, so neither half of a two-part claim rests on the other being green.
- **Verify:** shell cd .claude/skills/sdlc-studio && grep -q 'require-close' help/gate.md && grep -q 'require-close' reference-retro.md
- **Verified:** yes (2026-07-18)

### AC3: The rewritten line uses the shell verb and no longer passes on a misparse

- **Given** the previous line was `grep -q "..." <one file>`, where the `grep` verb takes no flags
- **When** the story is read back
- **Then** AC3 carries an explicit `shell` prefix (a compound check is not the single-pattern `grep` verb) and no bare `grep -q` form remains, so the flag can never again be consumed as the search pattern.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.US0166Ac3Tests
- **Verified:** yes (2026-07-18)

## Notes

The line as shipped read `grep -q "never at .deployed" <gate.md>`. The DSL `grep` verb takes
no flags, so `-q` was parsed as the PATTERN and the quoted text became a PATH. The verifier
therefore searched for the literal string `-q` across a list containing one file that does not
exist, found it, and exited 0. The AC was recorded green on every run without once checking
its own claim - and the claim happens to be true, which is why nothing ever surfaced it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored; the seeded AC3 about hardening the `grep` verb moved to its owning story US0228 |
