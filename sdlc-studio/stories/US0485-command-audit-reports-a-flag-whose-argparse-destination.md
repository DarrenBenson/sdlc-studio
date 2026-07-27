# US0485: command_audit reports a flag whose argparse destination no line ever reads

> **Status:** Ready
> **Delivers:** CR0448
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
> **Epic:** EP0175
> **Points:** 5

## User Story

**As a** operator trusting a documented flag to change what a command does
**I want** a flag whose destination is never read to be reported as dead
**So that** a flag cannot ship wearing live documentation while doing nothing

## Acceptance Criteria

### AC1: a flag whose destination is never read is reported

- **Given** a module defining a flag and passing its parsed value on without any line reading it
- **When** the detector runs
- **Then** it reports that flag, naming the module and the destination
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_flag_whose_destination_is_never_read_is_reported

### AC2: it is proven on the flag that motivated it

- **Given** gate's verify_batch exactly as it stood before US0479 deleted it, restored as a fixture
- **When** the detector runs over that fixture
- **Then** it reports verify_batch, so the defence is validated against the bug it defends against and not only against a convenient case
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_the_detector_catches_verify_batch_as_it_stood

### AC3: a flag that is read only through a defaulted lookup is still counted as read

- **Given** a flag whose value is read via a defaulted attribute lookup rather than a direct reference
- **When** the detector runs
- **Then** it does not report that flag, so a legitimate access pattern is not called dead
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_defaulted_lookup_counts_as_a_read

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
