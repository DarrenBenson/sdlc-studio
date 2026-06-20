# RV0002 - Adversarial Audit - v2.0.0 (skill profile)

> **Review type:** Adversarial multi-agent audit (skill profile: over-engineering / token-economy / determinism / external-benchmark)
> **Reviewer:** Adversarial Audit workflow
> **Date:** 2026-06-20
> **Project version:** 2.0.0
> **Proves:** RFC0002 (the general-purpose `/sdlc-studio audit` capability)

## Run summary

Four lenses, finders looping until dry over 3 rounds, then a 3-vote adversarial
refute panel (survive on >=2/3), then merge/classify.

| Metric | Value |
| --- | --- |
| Candidates found | 69 (3 rounds) |
| Survived the refute panel | 28 |
| Refuted | 41 (~59%) |
| Filed (after merge) | 18 - 4 Bug, 8 CR, 6 RFC |
| Cost | 221 agents, ~6M tokens, ~27 min |

The ~59% refute rate is the headline quality signal: the panel killed
plausible-but-wrong findings (e.g. "11 artifact types is too heavy" 0/3 - deliberate
depth; "use EARS not Given/When/Then" 0/3; "no placeholder-leak check" 1/3).

## Filed findings

**Bugs**

| ID | Sev | Finding |
| --- | --- | --- |
| BG0001 | High | Status vocabulary diverges across reference table, status-flow diagram and `sdlc_md.py` (Workflow `Complete` vs `Done`; CR `Blocked` - the one we added today - is not in the canonical table) |
| BG0002 | High | `reconcile.py` and `status.py` omit the bug and workflow artifact types from their census, contradicting the docs |
| BG0003 | **Critical** | `verify_ac.py` parses only `### AC` headings and silently ignores the bullet-AC style the parser otherwise supports - the oracle can miss AC |
| BG0004 | Medium | `review_prep` reads `personas.md` while the epic cascade reads `personas/` - inconsistent persona source |

**Change Requests** (clear, bounded)

| ID | Sev | Finding |
| --- | --- | --- |
| CR0002 | High | Deterministic duplicate-ID / collision detector (census silently collapses colliding IDs) |
| CR0003 | High | Referential-integrity check for required Epic/Story links and dangling ID refs |
| CR0004 | High | `review_prep` staleness uses mtime + raw-string time compare - non-deterministic across clones |
| CR0005 | Medium | `verify_ac` writes no dry-run report and keeps no run history |
| CR0006 | Medium | A graded / LLM-judge verifier verb for qualitative ACs |
| CR0007 | High | `epic implement --resume` from the workflow execution table |
| CR0008 | Medium | Collapse three-way config-defaults duplication into one authoritative source |
| CR0009 | Medium | Make best-practices guides sliceable / load-once |

**RFCs** (unsettled / structural)

| ID | Sev | Finding |
| --- | --- | --- |
| RFC0003 | High | Promote reconcile's mechanical apply into the script (today it is prose; the idempotency claim is false) |
| RFC0004 | Medium | `repo_map` ranking: Aider-style symbol-graph PageRank vs scope it down |
| RFC0005 | Medium | Optional project-constitution artifact with a machine-checkable principle gate |
| RFC0006 | Medium | Reconsider the default autonomous execution model (phase-gating, fresh-context isolation) |
| RFC0007 | Medium | Replace 13 baked-in fictional personas (~1680 lines) with template + generate-on-demand |
| RFC0008 | Medium | Consolidate the 5-file test reference clique (~2030 lines; two files unreachable from the router) |

## What this confirms

- **Determinism is the richest seam** (1 critical + 5 high findings). It validates
  RFC0001's "make guardrails deterministic" thesis and seeds RFC0003 (`reconcile --apply`).
- The audit caught a regression from *this morning*: BG0001 flags the CR `Blocked`
  status we back-ported as missing from the canonical table - exactly the drift a
  vocab-equality test would catch.
- BG0002 is self-demonstrating: `status` does not count bugs, so these very Bug
  artifacts will not appear in the dashboard until BG0002 is fixed.

## Recommended sequencing

1. **BG0003 (critical)** - verify_ac AC parsing; the oracle correctness underpins everything.
2. **BG0001, BG0002** - status/vocab integrity (cheap, high value, unblocks the dashboard).
3. **CR0002, CR0003 + RFC0003** - the determinism cluster (duplicate-ID, referential integrity, reconcile --apply).
4. The over-engineering RFCs (RFC0007, RFC0008) and remaining CRs as capacity allows.

## Relation to RFC0002

These 18 findings are the proving dataset for **RFC0002** (general-purpose
`/sdlc-studio audit`). The harness (find → 3-vote verify → merge → auto-file) and its
telemetry (refute rate, token cost, lens yield) are the evidence the RFC's design
decisions rest on. A second proving run with the **project profile** (pressure-testing
this repo's own PRD/TRD/TSD/personas/stories/code) is the recommended next instance.
