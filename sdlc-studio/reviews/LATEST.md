# LATEST - current project state (v2.4.1)

> The current-state anchor. **Re-read this and run `/sdlc-studio status` after any context reset
> or compaction.** Durable guidance lives in AGENTS.md; per-tranche detail lives in CHANGELOG.md
> and `sdlc-studio/retros/`; the original v2.0 unified review is `RV0001-unified-review-2026-06-20.md`.
>
> **Project version:** 2.4.1 · **Date:** 2026-06-22 · **Gates:** lint clean, 598 script tests pass,
> `gate` PASS, reconcile drift 0.

## Headline

The repo dogfoods the skill against its own source. Since the v2.0 brownfield extraction the skill
has grown an autonomous delivery loop and a deterministic control plane, a product layer, and a
self-checking maintenance surface - all built through its own autosprint loop with an independent
critic per unit.

## Shipped (high level - see CHANGELOG for the full list)

- **v2.1** autosprint + the deterministic control plane (ledger, loop guards, conformance gate,
  independent critic), complexity signals, audit harness, constitution, archival.
- **v2.2** version check + `skill-update`.
- **v2.3** Product Vision Document (multi-repo layer); deterministic artifact create/close +
  provenance; run telemetry; the portable CI `gate`; the doc-coverage Definition of Done; the
  Cooper goal-directed persona model + review-seat charters (RFC0016/RFC0017); help reframe.
- **v2.4** `project upgrade` (migrate a consuming project to current conventions); the advisory
  progressive-disclosure + best-practice check.

## State

- **Backlog:** the actionable CR/bug backlog is clear (all raised CRs/bugs through CR0063/BG0023
  are closed). RFCs accepted: RFC0001/0002/0014/0015/0016/0017; deferred: RFC0013 (deploy).
- **Known advisory backlog:** `scripts/disclosure.py` reports ~66 progressive-disclosure advisories
  (Load-when markers + orphans) - non-blocking; a future sweep is the token win.
- **Next options:** work the disclosure backlog; RFC0013 (deploy); or new product work.

## Operating reminders

- Trunk-based: small green commits to main, each gated on `npm run lint && npm test && gate`.
- Forward-port skill edits repo -> install targets via manual rsync (not `install.sh --local`).
- Stakes-scaled review (CR0061): full independent critic for code/risky units; lighter recorded
  review for pure-doc/mechanical ones.
