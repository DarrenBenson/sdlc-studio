# RFC-0014: run telemetry + a learning loop

> **Status:** Accepted
> **Priority:** Medium
> **Author:** Darren Benson (from the v2.2 usage retrospective)
> **Date:** 2026-06-21
> **Spans:** sdlc-studio skill (a telemetry recorder; autosprint close cascade; complexity calibration; RFC0009 WS5)
> **Related:** RFC0009 (WS5 wave-sizing, deferred for lack of cost data), reference-autosprint.md
> **Supersedes / Superseded by:** --

## Summary

The skill estimates effort and sizes waves but never captures what actually happened, so
calibration is a one-off manual study (as the 2026-06-21 complexity calibration was) and
RFC0009 WS5 (cost-weighted wave-sizing) stays blocked for lack of per-unit cost data.
Capture per-unit run outcomes locally so estimation, complexity calibration, and WS5
become continuous and self-improving - **privacy-first, no upload**.

## Context & Problem

Nothing records, per delivered unit: iterations to green, wall-time, stages passed,
critic verdict, whether it was later reopened/regressed, or token cost. So the loop can't
learn. WS5 explicitly waits on "per-story run-cost telemetry that doesn't exist."

## Goals / Non-Goals

**Goals**

- A standing, local capture of per-unit run outcomes the loop writes as it closes units.
- Feed it into estimation, the complexity/churn calibration (RFC0009), and unblock WS5.
- Privacy-first: local by default, opt-in for anything that leaves the machine.

**Non-Goals**

- Phone-home / mandatory telemetry. No upload by default.
- A metrics dashboard / external service.

## Design Options

### Option A - Local-only capture (privacy-first)

The autosprint close cascade appends a record per unit to `.local/telemetry.jsonl`
(`{id, type, iterations, wall_time_s, stages, critic_verdict, complexity, churn,
reopened}`); a `telemetry calibrate` derives estimation/complexity weights from it.
Nothing leaves the machine. **Pros:** safe, unblocks WS5, no trust ask. **Cons:**
per-project only - no cross-project model.

### Option B - Opt-in aggregation

A, plus an explicit opt-in to aggregate/upload anonymised metrics for a cross-project
model. **Pros:** better models. **Cons:** trust/privacy surface; off by default anyway.

### Option C - Status quo (one-off manual studies)

Calibrate by hand when needed (as today).

## Recommendation

**A.** Local-only `.local/telemetry.jsonl` written by the loop, consumed by calibration
and WS5; no upload. Revisit B only if a real cross-project need appears, and only opt-in.

## Open Decisions

| # | Decision | Options | Owner | Status |
| --- | --- | --- | --- | --- |
| D1 | What to capture | iterations + wall-time + stages + verdict + reopened **[leaning]**; tokens only if the runtime exposes them reliably to the script | Design | Resolved |
| D2 | Token cost | record when the agent can pass it (autosprint records it) / omit (not reliably available to a script) | Design | Resolved |
| D3 | Who records | the autosprint close cascade + `transition`/`close` | Design | Resolved |
| D4 | What consumes it | estimation, RFC0009 complexity calibration, WS5 wave-sizing | Operator | Resolved |
| D5 | Privacy default | local-only (A) **[leaning]** / opt-in aggregation (B) | Operator | Resolved |
| D6 | "Reopened/regressed" signal | a later transition off a terminal status, or a bug citing the unit's files (the calibration's defect signal) | Design | Resolved |

## Architecture Impact

| Layer | Impact | Change Type |
| --- | --- | --- |
| `scripts/telemetry.py` | `record` (append a run outcome) + `calibrate` (derive weights) | New |
| reference-autosprint.md / close cascade | record on each unit close | Enhancement |
| RFC0009 complexity weights / WS5 | consume telemetry instead of a one-off study | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Privacy / surprise upload | Low | High | local-only default; no network; opt-in for anything else |
| Token cost not reliably measurable | High | Medium | D2 - capture it only when the runtime provides it; iterations/time/defects work regardless |
| Goodhart (optimise the metric) | Medium | Medium | advisory weights; pair with the critic/verify oracle |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | `telemetry.py record` + the `.local/telemetry.jsonl` schema | CR (TBD) | D1, D5 |
| WS2 | Loop writes a record on each unit close | CR (TBD) | WS1, D3 |
| WS3 | `telemetry calibrate` -> estimation + complexity weights | CR (TBD) | WS1, D4 |
| WS4 | Unblock RFC0009 WS5 (cost-weighted wave-sizing) from real telemetry | CR (TBD) | WS3, RFC0009 |

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** Accepted, scoped to WS1-WS2 (telemetry.py record + .local/telemetry.jsonl; loop writes a record per unit close). WS3 (calibrate) + WS4 (RFC0009 WS5 unblock) deferred until data accrues.
**Rationale:** Start capturing per-unit run outcomes now so the dataset exists when calibration/WS5 are wanted; local-only, no upload. Open Decisions resolved to their leanings (D1 iterations+wall-time+stages+verdict+reopened, D2 tokens only when the runtime exposes them, D3 close cascade records, D5 local-only, D6 reopened signal); D4 deferred with WS3-4.
**Spawned CRs:** CR0050 (WS1), CR0051 (WS2).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - capture run outcomes to make calibration continuous and unblock RFC0009 WS5; privacy-first |
| 2026-06-21 | Darren Benson | Decision session: ACCEPTED scoped WS1-2 (spawns CR0050-CR0051); WS3-4 + D4 deferred until run data accrues |
