# US0531: The sweep detectors read the artefact corpus once per run and share it, so the cost is paid once rather than per unit

> **Status:** Draft
> **Delivers:** CR0465
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0181
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the sweep detectors read the corpus once per run

- **Given** a reconcile run over a workspace of N units
- **When** the sweep detectors execute
- **Then** the artefact corpus is opened once for the run rather than once per unit, and the opens do not scale with the unit count
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::CorpusReadOnceTests::test_the_corpus_is_read_once_per_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
