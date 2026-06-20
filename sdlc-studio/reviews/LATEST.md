# RV0001 - Unified Review - v2.0.0 + brownfield self-spec

> **Review type:** Unified PRD/TRD/TSD/Persona consolidation
> **Reviewer:** Darren Benson
> **Date:** 2026-06-20
> **Triggered by:** First review after brownfield extraction + RFC0001
> **Project version:** 2.0.0
> **Predecessor unified:** none (first)
> **Re-read this + run `/sdlc-studio status` after any context reset or compaction.**

## Headline

The repo dogfoods the skill against its own source. A brownfield (Generate mode)
extraction produced PRD, TRD, TSD, personas, 9 epics, 5 EP0005 stories, and
RFC0001 (Autonomous Delivery Loop, Draft). The first unified review (RV0001)
raised five findings; all are now actioned - see Post-review actions. Artifacts
are **Ready** (spec extracted, not yet test-validated), so nothing is Done.
Gates green: reconcile drift=0, lint exit 0, 181 script tests pass.

## Post-review actions (2026-06-20, same day)

- **CR0001 (Complete)** resolved P1 (command-vs-script scope note in PRD §3),
  P2 (Complete-vs-Ready note), T1 (corrected `reference-outputs.md` to the
  `> **Field:**` blockquote convention the parser reads).
- **S1 closed** - TSD generated (`tsd.md`); NFRs mapped to quality gates.
- **U1 closed** - four personas consulted on RFC0001 (consultation folded into
  the open decisions; personas now load-bearing).
- **Outstanding follow-up:** forward-port the T1 edit to the installed copy at
  `~/.claude/skills/sdlc-studio/reference-outputs.md` (CR0001 follow-up).

## Update 2026-06-20 - Autosprint fully delivered (RFC0001 Phase 1 + 2)

The autonomous delivery loop is **complete**. Phase 1 shipped the usable cut
(batch selector, conformance gate, policy doc, command wiring). **Phase 2 (CR0020)
now ships the hard guardrails, driven by autosprint over itself** (the loop
self-hosting): `ledger.py` (committed append-only decisions ledger, D4),
`loop_guard.py` (deterministic cap / repetition-breaker / completion oracle, D5/D2),
and the documented `--autonomous` mode (WS6) plus the independent critic (D3). All
via EP0007 stories US0009/US0010/US0011, each TDD'd and critic-approved; the
conformance check gated its own delivery (11/11). Closing gate run: reconcile drift
0, 210 script tests green, RETRO0001 written. **Next:** the 14 Proposed CRs are now
a candidate first real `autosprint --crs proposed` tranche (the loop on the backlog).

```text
══════════════════════════════════════════════════════════
                   DOCUMENT REVIEW SUMMARY
══════════════════════════════════════════════════════════

📋 PRD REVIEW (RV0001)        ~85% → P1/P2 fixed (CR0001)
📐 TRD REVIEW (RV0001)        ~90% → T1 fixed (CR0001)
🧪 TSD REVIEW                 now present (S1); awaiting first TSD review
👥 PERSONA REVIEW (RV0001)    ~85% → consulted on RFC0001 (U1)

──────────────────────────────────────────────────────────
📝 CHANGE REQUESTS

   CRs: 16 Proposed + 1 Complete   RFCs: 11 Draft   Bugs: 17 Open
   (CR0001 done; the rest from the skill audit RV0002 + project audit RV0003;
   RFC0009 = code-complexity signals; note BG0002 - status omits bugs)

──────────────────────────────────────────────────────────
🔗 CROSS-DOCUMENT CONSISTENCY

   PRD → TRD:              pass
   TRD → TSD:              now covered (TSD present; review pending)
   PRD → TSD:              now covered (NFRs gated in TSD; review pending)
   PRD → Persona:          pass
   Persona → CRs/Stories:  pass (consulted on RFC0001)
   Persona → Persona:      pass (no duplicates)

──────────────────────────────────────────────────────────
📌 PRIORITY ACTIONS (remaining)

   1. Triage the 18 audit findings (RV0002): BG0003 critical (verify_ac AC
      parsing) first, then BG0001/BG0002 (vocab + census), then the
      determinism cluster (CR0002/CR0003/RFC0003)
   2. Resolve RFC0001 and RFC0002 open decisions
   3. Forward-port the T1 edit to the installed copy (CR0001 follow-up)
   4. Deferred: remaining epics' stories; generate-mode test validation

──────────────────────────────────────────────────────────
🚀 PRODUCTION STATE

   SDLC Studio ships at v2.0.0, in production. This workspace is design and
   spec scaffolding (dogfood). No production risk. All gates green.
══════════════════════════════════════════════════════════
```

## Update 2026-06-20 - Determinism-hardening sprint COMPLETE (7/7)

First full `autosprint` tranche on the backlog, delivered end to end (RETRO0002),
each TDD'd + independent-critic-reviewed, trunk-based green:

- **Sprint-zero:** CR0016 (sharpened CR0003-CR0009's tautological AC) + CR0018 closed.
- **CR0003 / US0012:** `integrity.py` - referential-integrity (required links + dangling refs).
- **CR0021 / US0013:** `audit.py` + the new **tranche-audit** workflow step (step 2,
  before the triage STOP): weak-AC, unmet-deps, already-terminal, link-integrity.
- **CR0004 / US0014:** `review_prep` staleness from git `%cI` + datetime compare + warning.
- **CR0008 / US0015:** `config.py` - config-defaults.yaml single source (status.py reads it),
  12 doc fences removed, drift-guard test.
- **CR0007 / US0016:** `resume.py` - `epic implement --resume` from canonical Status.

The critic REJECTED 3 of 5 built units (real defects/honesty gaps), all repaired
before commit. Gates: reconcile drift 0, conformance 16/16, integrity 0 active
errors, 247 tests, installed in sync. Filed **BG0018** (reconcile misparses a
title that starts with a status word - surfaced by the closing reconcile).

**Backlog now:** 8 Proposed CRs (CR0005/0006/0009 + doc CRs CR0012-0017), all
audited **ready**; 1 Open bug (BG0018); 12 Draft RFCs (design track). Decisions
ledger: `decisions/determinism-sprint.md`.

## Update 2026-06-20 - Tooling-honesty + loop-integrity sprint COMPLETE (8/8)

Second autosprint tranche (bugs + high-value + quick wins), delivered end to end
(RETRO0003), each TDD'd + critic-reviewed, trunk-based green:

- **BG0019** - integrity + audit handle the `bug` class (links advisory; readiness by
  repro+fix) - cleared the RED integrity check the triage surfaced.
- **BG0018** - reconcile reads index status by table-header column, not a cell scan
  (a status-word title no longer misreads); systemic caller audit.
- **CR0023 / US0017** - conformance gate completed: Done now requires reconciled +
  critiqued (a committed independent-critic APPROVE via new `critic.py`). The gate
  blocked its own delivery until US0017's verdict was recorded.
- **CR0022 / US0018** - `autosprint plan` orders deps-first (topological, priority
  tiebreak; cycle aborts).
- **CR0012/13/14/17** - TRD/TSD doc-truth fixes.

Critic REJECT-then-fix twice (CR0023 reconciled scope, CR0022 prose-id edges). Gates:
reconcile drift 0, conformance 18/18, integrity clean, no collisions, 270 tests,
installed in sync.

**Backlog now:** 4 Proposed CRs (CR0005/0006/0009/0015), 0 Open bugs, 12 Draft RFCs
(design track; RFC0009 unlocks `--order wsjf`). Ledger: `decisions/tooling-honesty-sprint.md`.

## Known divergences

1. ~~Docs say "YAML frontmatter" vs the parser's `> **Field:**` headers~~ -
   **fixed** in `reference-outputs.md` (CR0001); forward-port to installed copy pending.
2. `review_prep.py` / `status.py` / `reconcile.py` reference docs over-claim vs
   the scripts' scope (CODE leg, `--full`, auto-fix, `--verify` are
   Claude-orchestrated). PRD §3 now notes this; the reference-doc wording itself
   is out of scope for CR0001 (tracked for a later doc pass).

## History

- [RV0001-unified-review-2026-06-20.md](RV0001-unified-review-2026-06-20.md) - first unified review (immutable).
- [RV0002-adversarial-audit-2026-06-20.md](RV0002-adversarial-audit-2026-06-20.md) - skill-profile audit: 69→28→18 filed; proves RFC0002.
- [RV0003-project-audit-2026-06-20.md](RV0003-project-audit-2026-06-20.md) - project-profile audit: 76→40→23 filed (13 Bug, mostly artifact contradictions); second RFC0002 proving run.
