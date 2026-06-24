# LATEST - current project state (v2.5.0)

> The current-state anchor. **Re-read this and run `/sdlc-studio status` after any context reset
> or compaction.** Durable guidance lives in AGENTS.md; per-tranche detail lives in CHANGELOG.md
> and `sdlc-studio/retros/`; the original v2.0 unified review is `RV0001-unified-review-2026-06-20.md`.
>
> **Project version:** 2.5.0 (+ unreleased v2.6.0 work) · **Date:** 2026-06-24 · **Gates:** lint
> clean, 850 script tests pass, `gate` PASS, reconcile drift 0, disclosure 0, npm audit 0, coverage 83%.
> **Command rename:** `autosprint` → `sprint` (CR0087; `autosprint` is a deprecated alias).

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
  progressive-disclosure + best-practice check; the disclosure backlog driven to **0**; the
  orchestrate-only **deploy** last-mile (RFC0013 WS1-3, gate/verify/record, never autonomous);
  Product Owner (PRD) + Product Manager (PVD) **review seats** with requirements-met sign-off; the
  hash-based **neutrality** lint guard; and a cluster of reconcile/parser fixes (multischema status,
  per-epic count blocks, verify_ac manual lines, project_upgrade safety).

## State

- **Backlog:** the actionable CR/bug backlog is clear (CRs through **CR0086** closed; 0 Proposed).
  RFCs accepted: RFC0001/0002/0013/0014/0015/0016/0017; **RFC0019** (authoring autosprint) is Draft.
  `disclosure` reports **0**.
- **Unreleased - greenfield + implementation DevEx (v2.6.0 work, dogfooded):** the
  greenfield-friction workstream (CR0077-CR0086), built by the skill's own autosprint loop from a
  field agent's greenfield + tranche-1 dogfooding. Authoring: lazy index creation + full-template
  scaffolds (CR0077), executable `init` (CR0079), batch create (CR0078), decisions log (CR0080),
  reconcile field projection (CR0082), greenfield runbook (CR0081). Implementation/conformance:
  the test-spec AC-to-test bridge (CR0085), the Definition-of-Done verify gate (CR0084), the
  cross-epic AC lint (CR0086), and agent-instructions that enforce the tool-first discipline
  (CR0083). All green + committed; not yet tagged.
- **Unreleased - the `sprint` lifecycle (RFC0019 Accepted, CR0087-0093):** dogfood-built next.
  `autosprint` renamed to **`sprint`** (CR0087; deprecated alias kept). The command is now the
  whole sprint lifecycle via the **goal ladder** `triage -> plan -> design -> done` (cumulative
  stop-points; NL maps to the furthest rung). New: `--goal plan` sprint planning (CR0091);
  greenfield **authoring** from a PRD - `sprint <prd.md> --goal design` drives PRD -> epics ->
  stories with two STOPs (CR0088-0090); `design` assigns story points (CR0092); a closing
  consistency pass over the backlog (CR0093). The loop is documented in `reference-sprint.md`.
- **Unreleased - sprint-2 hygiene + hardening (CR0094-0099, Part A stories):** dogfood-run via
  the sprint lifecycle (plan -> breakdown -> run). The 5 stale v2.0 Ready stories (US0001-0005)
  verified-and-closed - the Done-gate (CR0084) blocked a false close on a stale verifier, proving
  the loop. New: reconcile-before-plan (CR0094); `quality.done_requires_verified` toggle + status
  verify lane (CR0095); hard epic-scope test-spec requirement `verify_ac epic-ts` (CR0096);
  persona index-projection via a canonical field (CR0097); the audit flags **already-satisfied**
  Ready units (CR0098); **seat-scored WSJF** sprint planning (CR0099). LL0007 captured the
  planning learnings. 850 tests, gate clean.
- **In flight - review + optimise programme (to v2.5.0):** a dogfooded world-class review ran the
  audit skill-profile + the deterministic gates. Outcome: over-engineering and determinism are
  **clean** (the determinism candidates were refuted as false positives). The real backlog is two
  staged releases:
  - **v2.4.4 (harden + secure + DevEx):** shared-parser edge-case test battery + regression tests;
    test-density backfill (repo_map / github_sync / lessons); the 5 moderate npm vulns; a proper
    CONTRIBUTING dev-bootstrap (+ architecture pointer).
  - **v2.5.0 (consolidate + self-check):** collapse the 5 `reference-test-*.md` to ~3 + persona and
    quality-gate entry points + missing Progressive-Loading rows; a new advisory **doc-freshness**
    gate check; CI coverage + bandit; an RFC for vocabulary/verb-taxonomy/telemetry-surfacing.

## Operating reminders

- Trunk-based: small green commits to main, each gated on `npm run lint && npm test && gate`.
- Forward-port skill edits repo -> install targets via manual rsync (not `install.sh --local`).
- Stakes-scaled review (CR0061): full independent critic for code/risky units; lighter recorded
  review for pure-doc/mechanical ones.
