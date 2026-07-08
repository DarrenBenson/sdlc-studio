# US0066: Human sampling policy and triage-quality metrics

> **Status:** Ready
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0014
> **Persona:** Orchestrator / Operator
> **Source:** CR-0173 (workstream 2)

## User Story

**As an** operator sampling rather than gating
**I want** a config-driven sampling policy and triage-quality metrics
**So that** I audit the right subset and the numbers justify the sampling rate over time

## Acceptance Criteria

### AC1: Sampling policy fires correctly

- **Given** a fixture batch of triaged items
- **When** the policy runs (deterministic seed)
- **Then** every Critical is sampled, the configured percentage of the rest, and every
  raiser/triager severity disagreement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_sampling.py

### AC2: Metrics computed from the ledger

- **Given** the ledger over time
- **When** metrics are computed
- **Then** false-positive rate and severity inflation come from a script (no hand counting) and
  surface in status/telemetry
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_sampling.py -k metrics

## Design Notes (groomed 2026-07-08, see D0015)

- **Config (new `triage:` block, `config-defaults.yaml` + `reference-config.md`):**
  `sample_rate: 0.20` (of non-Critical), `always_sample: [Critical, disagreement]`,
  per-project overridable.
- **Sampling determinism:** seed the sampler so the test-over-fixture AC is reproducible.
- **Metrics from the ledger (no hand counting):** false-positive rate (triaged-valid later
  closed invalid) and severity inflation (raiser vs triage vs closure severity), surfaced in
  `status.py`/telemetry. Sampled-but-unreviewed shows as standing drift, not a one-time prompt.
- **Era-gated** under `schema_version: 3` (depends on US0065's `triaged` state).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | sdlc | Groomed to Ready: config defaults settled (D0015) |
