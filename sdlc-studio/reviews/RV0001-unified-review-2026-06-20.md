# RV0001 - Unified Review - v2.0.0 + brownfield self-spec

> **Review type:** Unified PRD/TRD/TSD/Persona consolidation
> **Reviewer:** Darren Benson
> **Date:** 2026-06-20
> **Triggered by:** First review after brownfield extraction + RFC0001
> **Project version:** 2.0.0
> **Predecessor unified:** none (first)

## Scope

First review pass over the newly extracted workspace: PRD, TRD, personas, 9
epics, 5 stories (EP0005), RFC0001. TSD absent (not generated). All gates green
at review time: `reconcile` drift=0, `npm run lint` exit 0, `npm test` 181 OK.

---

## PRD Review - verdict ~85%

| # | Severity | Finding | Action |
| --- | --- | --- | --- |
| P1 | Important | §3 Feature Inventory attributes Claude-orchestrated behaviour to scripts: Reconcile "auto-fix; --verify" and Review "CODE review, cadence" and Status "--full" point at `reconcile.py`/`review_prep.py`/`status.py`, but those scripts are narrower (detect-only / prep-only / pillars+hint). The EP0005 stories scope this correctly. | Tighten the Location/Description columns, or add a command-vs-script note. Candidate CR. |
| P2 | Important | Status tension: §3 says all features "Complete" while epics/stories are "Ready" and `status` shows 0% done. Defensible (implementation is complete; the extracted spec is unvalidated) but not stated. | Add one line distinguishing implementation-complete from spec-validated. |
| P3 | Suggestion | §10 already flags the markdown-flow test gap and §11 the open questions - good. Keep visible. | None; track. |

## TRD Review - verdict ~90%

| # | Severity | Finding | Action |
| --- | --- | --- | --- |
| T1 | Important | §6 records a real divergence: docs/templates say "YAML frontmatter" but the parser (`lib/sdlc_md.py`) reads `> **Field:**` blockquote headers. Flagged but unresolved. | Reconcile the docs to the parser (or vice versa) across templates + reference-outputs.md. Candidate CR. |
| T2 | Good | File counts now exact (reconcile aligned 72/42/31/19/10). The 5 ADRs are sound and match the source. | None. |

## TSD Review - verdict: absent (gap)

| # | Severity | Finding | Action |
| --- | --- | --- | --- |
| S1 | Important | No TSD exists. The generate-mode pipeline (philosophy steps 6-8) and the PRD §5 NFRs have no quality-gate home. | Deferred by design; generate when validation work begins. |

## Persona Review - verdict ~85%

| # | Severity | Finding | Action |
| --- | --- | --- | --- |
| U1 | Suggestion | 4 personas defined, 0 consulted (all "unused"). Load-bearing personas need at least one consultation or they become decoration. | Consult the four on RFC0001 (the live design). |
| U2 | Good | No duplicate personas; PRD §2 references all four. | None. |

---

## Cross-Document Consistency

| Check | Result |
| --- | --- |
| PRD → TRD | Pass - feature areas have architecture coverage; EP mapping consistent |
| TRD → TSD | Gap - no TSD |
| PRD → TSD | Gap - §5 NFRs have no quality gates |
| PRD → Persona | Pass - §2 references all four personas |
| Persona → CRs / Stories | Warn - none consulted yet (acceptable: workspace is one day old) |
| Persona → Persona | Pass - no duplicates |

## Epic / Story observations

- Only EP0005 has stories (5); the other 8 epics carry planned counts but no
  story files - deliberate deferral, recorded in the story index and LATEST.md.
- Generate-mode validation (tests against behaviour) not run, so every artifact
  is **Ready**, not Done - correct per `reference-philosophy.md`.

---

## Priority Actions

1. **Resolve RFC0001 open decisions D1-D6** (autonomy ceiling, stall-cap, oracle
   strength, ledger form, guardrail placement, commit-strategy coupling). Unblocks
   the loop workstreams.
2. **Raise a doc-tightening CR** covering P1 (script-vs-command scope) and T1
   (frontmatter vs blockquote parser). Both are content-accuracy, not mechanical
   drift, so out of reconcile's remit.
3. **Consult the four personas on RFC0001** (U1) to make them load-bearing.
4. **Deferred:** generate TSD, the remaining epics' stories, and run generate-mode
   test validation to move artifacts Ready → Done. Ideal first job for RFC0001's
   loop once built.

## Production State

SDLC Studio ships at v2.0.0 and is in production use. This `sdlc-studio/`
workspace is design and specification scaffolding that dogfoods the skill against
its own source. No production risk. All quality gates green at review time.
