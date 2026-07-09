# US0092: Block untraced spec-document edits at review

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0019
> **Persona:** QA seat
> **Affects:** scripts/spec_guard.py, reference-agent-prompt-template.md, templates/config-defaults.yaml, reference-config.md

## User Story

**As a** critic reviewing a delivery diff
**I want** a semantic edit to a requirements/spec document that no AC or ticket asked for to be surfaced as a blocking finding
**So that** a worker cannot falsify the source of truth to match a wrong implementation (the N=5 nd/Rn2 failure)

Closes CR0195. Era-gated behind `schema_version: 3`; dormant on v2. A requested spec edit stays legitimate; only an *untraced* one is blocking.

## Acceptance Criteria

### AC1: Config declares the spec-path globs

- **Given** `templates/config-defaults.yaml`
- **When** the review config is read
- **Then** a `review.spec_paths` glob list exists with a sensible default and is documented in `reference-config.md`
- **Verify:** grep "spec_paths" .claude/skills/sdlc-studio/templates/config-defaults.yaml

### AC2: A deterministic pre-check surfaces spec-path edits

- **Given** a changed-file set and the spec-path globs
- **When** `spec_guard.py` inspects it
- **Then** it deterministically reports which changed files match a spec glob (no model judgement in the match), a no-op unless schema v3
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_spec_guard.py::MatchTests

### AC3: The critic charter treats an untraced spec edit as blocking

- **Given** the critic/agent-prompt charter
- **When** a delivery diff touches a spec-glob path with no citing AC or explicit ticket ask
- **Then** the charter instructs that this is a blocking finding, not a style note; the traceability judgement stays with the critic while the pre-check guarantees the edit is surfaced
- **Verify:** grep "untraced spec" .claude/skills/sdlc-studio/reference-agent-prompt-template.md

### AC4: An untraced spec edit is exercised by a test

- **Given** a diff that edits a spec-glob file while no AC cites a spec change
- **When** the pre-check runs
- **Then** the edit is flagged for the critic; a matching AC-cited edit is reported as traced
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_spec_guard.py::TraceTests

### AC5: The new script is catalogued

- **Given** `scripts/spec_guard.py` ships
- **When** the docs floor is checked
- **Then** `reference-scripts.md` catalogues it
- **Verify:** grep "spec_guard.py" .claude/skills/sdlc-studio/reference-scripts.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0195 |
