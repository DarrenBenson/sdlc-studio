# US0577: A recorded review verdict carries the provenance of the brief it was given, so a hand-written prompt is detectable

> **Status:** Draft
> **Delivers:** CR0512
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0194
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the brief a seat was given is recorded with its verdict

- **Given** a seat briefed by `critic.py brief --unit BG0413 --seat engineering`
- **When** that verdict is recorded
- **Then** the row carries a stable fingerprint of the brief text the tool emitted, so the verdict can be traced to the prompt that produced it rather than asserted to have had one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefProvenanceTests::test_a_verdict_records_the_brief_it_was_given

### AC2: two different briefs give two different fingerprints

- **Given** the same unit briefed for two different seats
- **When** both verdicts are recorded
- **Then** their fingerprints differ, so the field identifies WHICH brief was used and cannot be satisfied by a constant
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefProvenanceTests::test_the_fingerprint_identifies_the_brief

### AC3: a hand-written prompt yields no provenance

- **Given** a verdict recorded by a caller that never invoked `critic.py brief`
- **When** the row is read back
- **Then** it carries no brief fingerprint, and the absence is distinguishable from a brief that produced an empty string
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefProvenanceTests::test_a_hand_written_prompt_records_no_provenance

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
