# US0062: Evidence-as-schema: per-type required evidence, lint-enforced

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0013
> **Persona:** Skill Maintainer
> **Source:** CR-0171
> **Depends on:** US0060

## User Story

**As a** sampling human auditor
**I want** the evidence-or-it-did-not-happen rule promoted to lint-enforced structure per type
**So that** every finding carries machine-checkable evidence before its quality is even assessed

## Acceptance Criteria

### AC1: Evidence required on a bug

- **Given** a bug with no file:line, command output, or reproduction
- **When** the lint runs
- **Then** it fails, naming the accepted evidence forms; placeholders count as absent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k "bug_without_evidence_fails or bug_with_file_line_passes"
- **Verified:** yes (2026-07-10)

### AC2: Legacy artefacts exempt (era-gated)

- **Given** an artefact predating schema v3
- **When** the lint runs
- **Then** it passes untouched
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k "v2_bug_exempt"
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-09-27 | Claude Opus 5.5 | BG0805: AC1 narrowed to its bug half and retitled; the CR half (a CR with no impact or effort estimate fails the lint) is retired by BG0756 (a3cee21a), which made the evidence-present rule bug-only. Its -k terms `cr_without_effort_fails` and `cr_with_impact_and_effort_passes` selected nothing: 2353eee9 (2026-07-15) renamed them to `cr_without_a_size_fails` and `cr_with_impact_and_points_passes`, and BG0756 deleted those. The bug terms stand. |
