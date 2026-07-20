# US0261: Count review rounds on the run state and refuse another past a configured ceiling without explicit operator confirmation

> **Status:** Ready
> **Delivers:** CR0358
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml
> **Epic:** EP0085
> **Points:** 3

## User Story

**As an** operator paying for a close review
**I want** the loop to count its rounds and stop to ask me once it passes a configured ceiling
**So that** an unbounded repair loop cannot spend my budget without anyone deciding it should

## Acceptance Criteria

### AC1: A recorded review round increments a counter on the run state

- **Given** an open run with no review rounds recorded
- **When** a review verdict is recorded for the run
- **Then** the run state carries a review-round count of 1, and a second recorded verdict makes it 2
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_recording_a_verdict_increments_the_run_review_round
- **Verified:** yes (2026-07-20)

### AC2: Past the ceiling, a further round is refused rather than started

- **Given** a run whose recorded review-round count has reached the configured ceiling
- **When** another review round is requested
- **Then** it is refused, naming the count, the ceiling and the override, and no brief is generated
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_round_past_the_ceiling_is_refused
- **Verified:** yes (2026-07-20)

### AC3: The ceiling is configurable with a shipped default

- **Given** a project with no explicit setting
- **When** the ceiling is resolved
- **Then** it comes from `review.max_rounds` in config with a shipped default, and an explicit project setting overrides it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_ceiling_resolves_from_config_with_default
- **Verified:** yes (2026-07-20)

### AC4: The override is explicit, recorded, and never implicit

- **Given** a refused round past the ceiling
- **When** the operator confirms the extra round explicitly
- **Then** the round proceeds and the run state records that the ceiling was overridden and at which round, so the retro can read it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_ceiling_override_is_explicit_and_recorded
- **Verified:** yes (2026-07-20)

### AC5: A run that never opened does not silently count rounds into nothing

- **Given** no open run
- **When** a verdict is recorded
- **Then** the verdict is still recorded and the absence of a run is reported, never a phantom count written against a null run id
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_verdict_without_an_open_run_reports_rather_than_counts
- **Verified:** yes (2026-07-20)

## Notes

`run-state.json` lives under `sdlc-studio/.local/` and is **not** one of the on-disk
surfaces in `reference-schema.md`, so adding the round-count fields needs no
`schema_version` bump. Extend `run_state.FIELDS` and `_blank()` together - a field absent
from `_blank()` is a `KeyError` on any run opened before this story.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-20 | sdlc-studio | Groomed: user story and ACs authored against the critic/run_state surface |
