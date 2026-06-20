# RFC-0002: Adversarial Audit (`/sdlc-studio audit`) as a first-class capability

> **Status:** Draft
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill (new command/mode, reference doc, prompt harness, optional scripts)
> **Related:** RFC0001 (autonomous loop), reference-review.md, reference-reconcile.md, reference-verify.md, reference-consult.md
> **Supersedes / Superseded by:** --

## Summary

Promote the adversarial-review harness proven on 2026-06-20 into a **project-agnostic**
capability: `/sdlc-studio audit` runs a multi-agent adversarial pressure-test over a
project's whole artifact graph - PRD, TRD, TSD, personas, epics/stories (AC quality),
code (vs AC), design/RFCs, and cross-artifact traceability - verifies each candidate
with an independent refute panel, and auto-files Bugs/CRs/RFCs from the survivors. The
skill's own self-audit is one **lens profile** of the same harness.

## Context & Problem

The existing quality commands check **consistency**: `review` consolidates PRD/TRD/TSD/
persona, `reconcile` fixes status/index drift, `verify_ac` checks AC against code. None
of them hunt adversarially for **weakness and incoherence** - vague or untestable AC,
requirements with no acceptance signal, architecture that has drifted from the code,
rotted ADRs, personas that are never consulted, spec-vs-code gaps, broken traceability.

A one-off run on 2026-06-20 proved the harness works on real artifacts:

- 4 lenses × loop-until-dry finders → **69 candidates** in 3 rounds.
- A 3-vote adversarial refute panel (survive on >=2/3) cut that to **28 survivors**
  (**41 refuted, ~59%**) - the refutations correctly killed plausible-but-wrong items
  (e.g. "11 artifact types is too heavy" 0/3, deliberate depth).
- A merge/classify step produced **18 filed findings** (4 Bug, 8 CR, 6 RFC).
- Cost: **221 agents, ~6M tokens, ~27 min** for the skill profile.

The harness is currently a hand-authored workflow script. This RFC asks whether and how
to make it a repeatable skill feature, and (crucially) **project-agnostic** rather than
skill-specific.

## Goals / Non-Goals

**Goals**

- A repeatable `audit` that pressure-tests any SDLC Studio project's artifact graph.
- Pluggable **lens profiles**: a default *project* profile (per-artifact-type lenses +
  cross-artifact coherence) and a *skill* profile (over-engineering / token-economy /
  determinism / external-benchmark - the four lenses run on 2026-06-20).
- The refute panel as a built-in guard against false positives (the 59% refute rate is
  the feature, not a flaw).
- Auto-file or triage, configurable; findings typed Bug/CR/RFC by the standard rule.

**Non-Goals**

- Replacing `review`, `reconcile`, `verify_ac`, `consult`, or `code review` - `audit`
  composes with them (it is the adversarial superset, they remain the cheap passes).
- Implementing the findings it raises (that is downstream CR/RFC work).
- Mandating one harness runtime (portability is an open decision, see D2).

---

## Design Options

### Option A - Documented prompt harness + profile packs (portable)

**Approach:** ship `reference-audit.md` (the methodology: lenses, profiles, refute
panel, taxonomy, filing) + per-profile lens packs as prompt templates. The operator (or
any AGENTS.md tool) drives it; no runtime dependency.
**Pros:** tool-neutral; ships now; mirrors RFC0001 Option A.
**Cons:** orchestration quality depends on the harness the tool provides.
**Effort / risk:** Low / low.

### Option B - `/sdlc-studio audit [scope] [--profile]` command

**Approach:** a first-class command that runs the find → verify → merge → file pipeline,
with `--scope prd,trd,...`, `--profile project|skill`, `--auto-file|--triage`, `--budget`.
**Pros:** one entry point; consistent; composes with review/reconcile/verify.
**Cons:** larger surface; needs the multi-agent runtime.
**Effort / risk:** Medium / medium.

### Option C - `review --adversarial` mode

**Approach:** extend the existing `review` rather than add a command.
**Pros:** no new command; reuses review's doc-chain plumbing and LATEST.md anchor.
**Cons:** conflates a cheap consolidation pass with an expensive adversarial one;
muddies `review`'s contract.
**Effort / risk:** Medium / low.

---

## Recommendation

**Option A now (portable methodology + profile packs), then Option B** as the command
that wraps it, with deterministic helpers (ID allocation, filing, index rebuild) reused
from the scripts. Keep it a distinct `audit`, not a `review` mode (Option C), so the
cheap and expensive passes stay separable. The skill profile is the first packaged
profile; the project profile is the headline.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Command vs mode | new `audit` command **[leaning]** / `review --adversarial` | Operator | matches Option B/A | Open |
| D2 | Harness runtime | Workflow tool (Claude-only) / portable prompt harness (tool-neutral) **[leaning]** / both | Design | tool-neutrality vs power; lean portable-first | Open |
| D3 | Verify threshold | 3-vote >=2/3 **[proven]** / N-of-M configurable / per-severity | Design | the run validated 3-vote; make N configurable | Open |
| D4 | Filing default | auto-file **[run default]** / triage-then-approve / per-severity (auto low-risk, triage structural) | Operator | balance speed vs control | Open |
| D5 | Lens profiles | which per-artifact lenses ship in the project profile; how packs are declared/extended | Design | derive from the per-type pressure-tests below | Open |
| D6 | Token budget per profile | hard cap + loop-until-dry round limit; the skill profile cost ~6M tokens | Operator | set a default budget; expose `--budget` | Open |

### Project-profile lens packs (D5 seed)

| Artifact | Adversarial lens |
| --- | --- |
| PRD | untestable/vague requirements; features with no acceptance signal; scope contradictions |
| TRD | architecture-vs-code drift; unjustified choices; rotted ADRs; missing failure/scaling story |
| TSD | coverage gaps; NFRs with no gate; gates that do not run |
| Personas | not load-bearing; contradictory needs; stale; duplicate |
| Epics/Stories | ambiguous AC; no edge cases; AC not machine-checkable; Ready criteria unmet |
| Code | does not satisfy claimed AC; correctness/security smells; pattern violations |
| Design/RFC | open decisions rotting; accepted-without-spawned-CRs; options never weighed |
| Cross-artifact | broken PRD→epic→story→code→test traceability; epic Done with non-Done stories |

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| `reference-audit.md` | New methodology + profile packs | New |
| `templates/automation/` | Audit prompt harness templates | New |
| `audit` command (or `review --adversarial`) | New entry point | New / Enhancement |
| Filing helpers | Reuse `next_id.py`; deterministic Bug/CR/RFC writer + index rebuild | New (relates to the audit's own determinism findings) |
| SKILL.md / help | Router + help entry | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Token cost (skill profile ~6M) makes routine use prohibitive | High | Medium | `--budget`, round caps, `--scope`, cheaper default profile, run on demand not in CI |
| False positives file busywork | Medium | Medium | the refute panel (proven 59% cull); merge step; triage option |
| Finding sprawl (18 from one run) overwhelms the backlog | Medium | Medium | severity ranking; merge; per-severity filing default (D4) |
| Overlap with review/reconcile/verify confuses users | Medium | Low | clear contract: audit = adversarial weakness-hunt, the others = consistency |

---

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | `reference-audit.md` methodology + project lens packs | CR (TBD) | D1, D5 |
| WS2 | Portable prompt harness templates (Option A) | CR (TBD) | WS1, D2 |
| WS3 | Deterministic filing helper (Bug/CR/RFC writer + index rebuild) | CR (TBD) | - |
| WS4 | `audit` command wiring (Option B) + SKILL.md/help | CR (TBD) | WS1-WS3, D1 |
| WS5 | Skill-profile pack (the four lenses) packaged | CR (TBD) | WS1 |

---

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** TBD
**Rationale:** TBD
**Spawned CRs:** TBD

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC | RFC-0001 | Autonomous Delivery Loop | Draft | sibling (shares the verify-panel idea) |
| Review | RV0002 | Adversarial audit run (this run's findings) | - | proving instance |
| Reference | -- | reference-review.md / reference-reconcile.md / reference-verify.md | Live | composes with |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | RFC drafted from the 2026-06-20 self-audit run (69→28→18; 41 refuted; 221 agents) |
