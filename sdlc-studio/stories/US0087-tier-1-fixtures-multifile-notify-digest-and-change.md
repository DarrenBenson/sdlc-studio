# US0087: Tier-1 fixtures: multifile-notify-digest and change-request-ledger-drift

> **Status:** Draft
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Sam Eriksson (QA)
> **CR:** CR-0193

## User Story

**As a** benchmark operator
**I want** two fixtures sized past the pipeline's engagement threshold, each targeting one differentiating claim
**So that** the benchmark can detect hidden-requirement discovery and drift control instead of measuring nothing

## Acceptance Criteria

### AC1: multifile-notify-digest exercises hidden-requirement discovery

- **Given** the fixture's visible workspace (~7 interdependent files + docs/SPEC.md with ~10 numbered requirements) and an under-specified digest-mode ticket
- **When** the hidden suite runs against a ticket-text-only reference implementation
- **Then** the spec-interaction tests fail (urgent bypass, mandatory-only for unsubscribed, quiet-hours deferral, throttle counts sends, audit reason codes) while the happy path passes
- **Verify:** manual validation record - hidden suite red on the naive variant, green on the full reference solution

### AC2: change-request-ledger-drift exercises drift control

- **Given** the fixture's ~6-file ledger module, its ~8-rule SPEC, and a CR ticket relaxing one rule
- **When** the hidden suite runs against the tempting-but-wrong reference variant (normalisation breaking adjacent rules)
- **Then** the regression tests on unchanged rules fail; the correct reference passes all, including the deterministic spec-updated check
- **Verify:** manual validation record - hidden suite red on the seeded variant, green on the reference

### AC3: Fairness invariant holds

- **Given** both fixtures
- **When** reviewed
- **Then** everything needed to pass each hidden suite is present in the visible workspace (spec + code); nothing requires sdlc-studio artifacts to discover
- **Verify:** manual independent review sign-off

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sprint: CR0193 | Created via `new` (deterministic) |
