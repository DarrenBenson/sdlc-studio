# RFC-0026: Difficulty-aware model-tier routing for delegated workers

> **Status:** Accepted
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Raised-by:** operator vision + benchmark spike (D0012)
> **Related:** RFC0009 (complexity signals), RFC0025 (benchmark), CR0178 (harness)

## Summary

The sprint loop fans work units out to delegated workers, all at the session's own model
regardless of how hard the unit is. Add **difficulty-aware model-tier routing**: a
deterministic estimator scores each unit's difficulty from existing signals (blast-radius
cognitive complexity, churn-weighted risk, file scope, spec size, novelty) and recommends an
abstract model tier (`tiny/small/medium/large/xlarge`) that the project maps to its own model
identifiers. Cost efficiency becomes a measurable, benchmarkable property of the pipeline
rather than an accident of whatever model the session happened to run.

## Context & Problem

Two pressures converge here. First, waste: a one-line config fix and a cross-cutting parser
change currently cost the same per-token rate, because every delegated worker inherits the
orchestrator's model. Second, evidence: the N=1 benchmark spike (D0012) found the pipeline's
current fixtures could not demonstrate value against plain Claude Code; cost-at-equal-quality
is one of the few axes where a disciplined pipeline can show a mechanical advantage, but only
if routing exists to create the cost difference. The skill already computes the inputs
(RFC0009's `complexity.py assess`, story points, AC counts) - nothing consumes them for
model selection.

The skill is ecosystem-neutral: it runs under Claude Code, Codex, Cursor, Gemini and others,
so tiers must be abstract names mapped to opaque model-identifier strings the orchestrating
agent passes to its own spawn mechanism. The skill never calls a model API.

## Goals / Non-Goals

**Goals**

- A deterministic, reproducible difficulty score per work unit, from signals already on disk.
- An abstract five-tier vocabulary with a project-declared model map, degrading safely when a
  project declares fewer tiers.
- Advisory routing recommendations in the sprint plan (`tier`, `model` per unit), consumed by
  the orchestrator when spawning workers; never a gate.
- An escalation rule for when a routed worker fails, bounded by the existing loop_guard cap.
- Per-tier telemetry so routing quality (escape rate, escalation rate per tier) becomes
  measurable - feeding both calibration and the benchmark.

**Non-Goals**

- Calling model APIs or holding pricing data inside the skill payload (pricing lives in the
  repo-only bench tooling).
- Routing the orchestrator itself, the closing-gate adversarial critic, or authoring/design
  workers (v1 routes code-delivery workers: build, test, per-unit critic).
- A model-judged ambiguity/novelty rubric (deferred until per-tier telemetry shows where the
  deterministic score mis-routes).

---

## Design Options

### Option A - deterministic estimator, advisory routing, upward-degrading tier map (recommended)

**Approach:** a new sibling script `scripts/route.py` (estimate / pick / escalate / tiers)
scoring difficulty 0-100 from `complexity.assess` blast-radius signals + artifact fields
(AC count, story points, files affected, unresolved-path novelty), banded to five tiers via
configurable thresholds. `sprint.py plan` stamps `difficulty` (always) and `tier`/`model`
(when `routing.enabled`) next to the existing `token_budget`. The orchestrator passes the
model id to its own spawn mechanism; overrides are recorded in the ledger.
**Pros:** reproducible; zero extra tokens at plan time; tool-neutral; builds on RFC0009
machinery already calibrated against this repo's defect history.
**Cons:** blind to ticket ambiguity/novelty beyond the unresolved-path proxy; thresholds need
calibration from telemetry over time.
**Effort / risk:** M; main risk is under-routing (a too-small model on a hard unit), mitigated
by the missing-signal 0.5 default, the low-confidence upward bump, kind floors, and escalation.

### Option B - model-judged difficulty rubric per unit

**Approach:** the orchestrator (or a seat consult) scores each unit against a short rubric
(ambiguity, novelty, blast radius) at plan time; deterministic signals feed in as context.
**Pros:** sees what deterministic signals cannot (vague ACs, novel domains).
**Cons:** costs tokens per planning pass; non-reproducible; the judge model itself becomes a
calibration variable; violates cheap-plan doctrine for large batches.
**Effort / risk:** M-L; rejected for v1, kept as the documented v1.1 side-channel
(`.local/difficulty-inputs.json`, same pattern as `wsjf-inputs.json`) once telemetry
justifies it.

### Option C - no routing; scale token budget only (status quo plus)

**Approach:** keep single-model workers, extend the existing `token_budget` scaling.
**Pros:** zero new surface.
**Cons:** token budget does not change the per-token rate; the cost axis stays unmeasurable;
declines the operator's stated direction.
**Effort / risk:** nil; rejected.

---

## Recommendation

Option A, with Option B's rubric as a documented deferred side-channel.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Estimator: deterministic vs hybrid rubric | deterministic-only / +rubric | operator | operator call | Resolved - deterministic v1, rubric hook documented for v1.1 |
| D2 | Critic tier relative to author | match+floor / always above | operator | operator call | Resolved - match author, floored at medium for code/security/data-loss; independence stays the enforced floor |
| D3 | Tier vocabulary size | 5 sparse-friendly / 3 | operator | operator call | Resolved - 5 tiers (tiny/small/medium/large/xlarge); undeclared tiers degrade UPWARD to nearest declared larger, never downward |
| D4 | Escalation budget | shares loop_guard 3-attempt cap / separate budget | design | this RFC | Resolved - shares the cap; retry once at assigned tier, then escalate one declared tier; loop_guard arithmetic untouched |
| D5 | Emission when routing disabled | nothing / difficulty only / tier too | design | this RFC | Resolved - `difficulty` always emitted (advisory info); `tier`/`model` only when `routing.enabled` |
| D6 | Scope of routed workers in v1 | delivery only / + authoring | design | this RFC | Resolved - code-delivery workers only (build, test, per-unit critic); authoring/design workers out of scope |

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| `scripts/route.py` | New estimator/pick/escalate/tiers helper | New |
| `scripts/lib/sdlc_md.py` | Shared `affects_files` + `count_acs` helpers lifted from sprint.py/audit.py | Enhancement |
| `scripts/sprint.py` | Plan enrichment (difficulty/tier/model) for both orders | Enhancement |
| `scripts/telemetry.py` | `tier_recommended/tier_delivered/model/escalated` fields + per-tier summary | Enhancement |
| `.config.yaml` schema | New `routing:` block (enabled, models, floor, critic_tier, thresholds, escalation) | New |
| `reference-sprint.md`, `reference-agent-prompt-template.md` | Routing policy + consumption prose | Enhancement |
| `tools/bench/` (repo-only) | Arm R + cost index | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Under-routing sends a hard unit to a small model | Medium | Medium | Missing-signal 0.5 default; low-confidence upward bump; kind floors; retry-then-escalate; per-tier escape telemetry |
| Threshold cutpoints miscalibrated at launch | High | Low | Advisory-only; configurable `routing.thresholds`; telemetry feedback loop |
| Orchestrators ignore the recommendation silently | Medium | Low | Override-goes-to-ledger rule (model-instructed); tier_recommended vs tier_delivered recorded in telemetry |
| Tier map abused as a hard gate by a consuming project | Low | Medium | Doctrine prose: advisory, never read by any gate |

---

## Phased Plan / Workstreams

| WS | Workstream | Repo | Becomes | Depends on |
| --- | --- | --- | --- | --- |
| WS1 | Routing foundation: route.py + lib helpers + config block + docs + tests | this | CR (routing foundation) | - |
| WS2 | Plan integration: sprint.py enrichment + reference prose | this | CR (plan integration) | WS1 |
| WS3 | Feedback loop: telemetry tier fields + per-tier summary | this | CR (feedback loop) | WS1 |
| WS4 | Bench tie-in: arm R + cost index (repo-only) | this | CR (bench arm R) | WS1-WS3 |

---

## Decision

**Outcome:** Accepted - Option A (deterministic estimator, advisory routing, upward-degrading
five-tier map), with Option B's rubric documented as the deferred v1.1 side-channel.
**Rationale:** Reproducible and free at plan time; builds on the already-calibrated RFC0009
complexity machinery; tool-neutral by construction (opaque model ids, no API calls); the
advisory-first + telemetry-feedback shape matches how every other signal in the skill was
adopted (constitution, provenance, conformance). Cost-at-equal-quality becomes a measurable
benchmark axis via arm R.
**Spawned CRs:**
[CR-0189](../change-requests/CR0189-routing-foundation-route-py-difficulty-estimator-tier-map.md) (WS1),
[CR-0190](../change-requests/CR0190-sprint-plan-enrichment-difficulty-tier-and-model-per.md) (WS2),
[CR-0191](../change-requests/CR0191-routing-feedback-loop-per-tier-telemetry-and-escalation.md) (WS3),
[CR-0192](../change-requests/CR0192-benchmark-arm-r-routed-pipeline-variant-with-cost.md) (WS4).

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC | RFC-0009 | Code-complexity signals | Accepted | supplies the estimator's code signals |
| RFC | RFC-0025 | Evidence and benchmark harness | Accepted | consumes routing via arm R / cost index |
| CR | CR-0178 | Benchmark harness implementation | Complete | harness arm R extends |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | operator + sdlc | Drafted with all open decisions resolved in-session (operator answered D1-D3 directly; D4-D6 settled by design review); accepted |
