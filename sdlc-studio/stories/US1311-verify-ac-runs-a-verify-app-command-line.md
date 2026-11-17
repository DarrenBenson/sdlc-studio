# US1311: `verify_ac` runs a `Verify: app <command>` line and records the evidence files it wrote, failing a command that exits 0 with no evidence

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0738
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_app_evidence.py, changelog.d/US1311.md
> **Epic:** EP0375
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `verify_ac` runs a `Verify: app <command>` line and records the evidence files it wrote, failing a command that exits 0 with no evidence
**So that** CR0738 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: An app verifier passes on exit 0 with evidence, and records it

- **Given** a criterion `Verify: app python3 drive.py`, where `drive.py` writes a screenshot to the folder named by `SDLC_EVIDENCE_DIR` and exits 0
- **When** `verify_ac.py` runs the unit
- **Then** the criterion passes and the verify report records the evidence file's path, under `sdlc-studio/evidence/app/<unit>/`. Fails on: the command run without the folder set, or a pass with no path recorded
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_app_evidence.py::AppVerifierTests::test_an_app_command_that_writes_evidence_passes_and_is_recorded

### AC2: No evidence or a non-zero exit fails

- **Given** one command that exits 0 and writes nothing, and one that writes a file and exits 1
- **When** `verify_ac.py` runs each
- **Then** both fail; the first names the folder it looked in. Fails on: exit 0 alone taken as a pass, so an app check that drove nothing goes green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_app_evidence.py::AppVerifierTests::test_no_evidence_or_a_non_zero_exit_fails

### AC3: Stale evidence does not count, and the verifier is documented

- **Given** a file left in the unit's evidence folder by an earlier run and a command that writes nothing new
- **When** `verify_ac.py` runs it
- **Then** it fails as having no evidence, and `reference-verify.md`'s verifier table lists `app` with what it passes on. Fails on: an earlier run's screenshot passing today's criterion
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_app_evidence.py::AppVerifierTests::test_stale_evidence_does_not_count

## Notes

- The command is the project's own (D0518): the skill ships no browser driver. `deploy` is the orchestrate-only pattern to follow.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
