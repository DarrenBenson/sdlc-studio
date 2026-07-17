# US0199: brief --rejoinder quotes the prior verdict verbatim with the re-execute-your-probes instruction and return contract; a malformed prior-verdict file is refused

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0069
> **Points:** 2

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the re-verdict loop's scaffolding emitted deterministically from the prior verdict
**So that** every REJECT-repair cycle re-reviews against the same complete brief, and the re-run-your-mutants demand stops being optional

## Acceptance Criteria

### AC1: the rejoinder brief is emitted from the prior verdict

- **Given** a recorded prior verdict file with VERDICT/ISSUES/BLOCKING, and a malformed one
- **When** `critic.py brief --unit USxxxx --seat qa --rejoinder <prior-verdict-file>` runs against each
- **Then** brief --rejoinder emits the prior verdict block verbatim plus the re-execute-your-probes instruction and the return contract; a malformed prior-verdict file is refused
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_critic.py -k Rejoinder
- **Verified:** yes (2026-07-17)

### AC2: the brief demands re-running the named probes before approval

- **Given** a prior verdict naming the probes and mutants it executed
- **When** the rejoinder brief is emitted
- **Then** The rejoinder brief instructs the reviewer to re-run previously named mutants/probes before approving - the lesson from the two vacuous killing tests, in the ceremony not just the lore
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_critic.py -k RejoinderProbe
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
