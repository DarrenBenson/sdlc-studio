# US0194: critic records adversarial evidence distinct from verdicts; conformance critiqued requires evidence plus a non-author sign-off with recorded delegate chain and the embedded decision brief

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-workflow-personas.md
> **Epic:** EP0064
> **Points:** 5

## User Story

**As** Jonah Reyes (team lead)
**I want** the two-role review model (seat subagent finds, independent principal signs) enforced as machinery
**So that** no unit closes on an uninformed or self-controlled sign-off, and the delegation chain is on the record

## Acceptance Criteria

### AC1: evidence and verdict are distinct; the critiqued stage requires both

- **Given** a unit reviewed by a seat subagent and a sign-off recorded by a principal
- **When** critic.py records the adversarial pass and conformance evaluates the critiqued stage
- **Then** critic.py records the adversarial pass as evidence distinct from the verdict; conformance critiqued requires evidence + a sign-off whose principal differs from the author AND from the authoring session's subagents
- **Verify:** manual - retired by US0940: US0918 (2bc6eb15) retired `critic.py evidence` and deleted `record_evidence` with `EvidenceTests`, so no adversarial pass is recorded as evidence apart from its verdict; `critiqued` now reads one independent delivery verdict or a frozen batch row, and the signature is one per run at `sprint sign` (US0919)
- **Verified:** manual (2026-09-26) - retired, superseded by US0918

### AC2: a delegated sign-off carries its chain; a self-controlled delegate is refused

- **Given** a sign-off delegated by the operator to a named principal in a separate trust boundary
- **When** the delegated verdict is recorded
- **Then** Delegated sign-off carries the recorded chain (operator -> delegate, trust boundary named); an authoring-session subagent as delegate is refused loudly
- **Verify:** manual - retired by US0919: the per-unit sign-off, its delegated route and `critic.py signoff-brief` are retired; the operator reads the run's report and signs it once at `sprint sign`
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

### AC3: the sign-off request embeds the decision brief

- **Given** a run ready for the reviewer-of-record ask
- **When** the sign-off request is composed
- **Then** The sign-off request embeds the CR0318 decision brief (deliveries, critic REJECTs + repairs, gate/cost evidence) with approve/hold/delegate paths
- **Verify:** manual - retired by US0919: the per-unit sign-off, its delegated route and `critic.py signoff-brief` are retired; the operator reads the run's report and signs it once at `sprint sign`
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
| 2026-09-25 | US0919 | AC2 and AC3 retired in the D0259 pattern: the per-unit sign-off, its delegated route and `critic.py signoff-brief` are retired; the operator reads the run's report and signs it once at `sprint sign` |
| 2026-09-26 | US0940 | AC1 retired in the D0259 pattern: US0918 deleted the evidence ledger it recorded into, without retiring this stamp |
