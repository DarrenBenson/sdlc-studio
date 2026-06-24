# LATEST - current project state (v3.0.1)

> The current-state anchor. **Re-read this and run `/sdlc-studio status` after any context reset
> or compaction.** Durable guidance lives in AGENTS.md; per-tranche detail lives in CHANGELOG.md
> and `sdlc-studio/retros/`; the original v2.0 unified review is `RV0001-unified-review-2026-06-20.md`.
>
> **Project version:** 3.0.1 (the consolidated v3 line, released 2026-06-24) · **Date:** 2026-06-24 ·
> **Gates:** lint clean, 876 script tests pass, `gate` PASS, reconcile drift 0, disclosure 0,
> npm audit 0, coverage 83%.
> **v3.0.1 folds the whole v3 line into one release** (the per-fix v3.0.x/v3.1/v3.2 tags were
> consolidated away to keep version numbers low): the `autosprint`→`sprint` rename + sprint
> lifecycle + greenfield authoring + RV0005 self-review, then the field-dogfood fixes - BG0035
> (per-table duplicate-id), BG0036 (`init` gitignores `.local/`), CR0106 (`sprint plan --epic`),
> CR0107 (dependency waves), BG0037 (verify-report merge), CR0109 (audit lint), CR0110 (design-time
> TS matrix), CR0111 (`verify_ac --batch`), plus the DX pass - **CR0108** (natural-language
> "You can just ask" help blocks) and **CR0112** (stripped internal provenance tags from
> consuming-facing docs + a guard).
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

- **Backlog:** the actionable CR/bug backlog is clear (CRs through **CR0105** closed; 0 Proposed;
  BG0034 fixed). RFCs accepted: RFC0001/0002/0013/0014/0015/0016/0017/**0019**. `disclosure` **0**.
- **v3.0.1 - greenfield + implementation DevEx (v2.6.0 work, dogfooded):** the
  greenfield-friction workstream (CR0077-CR0086), built by the skill's own autosprint loop from a
  field agent's greenfield + tranche-1 dogfooding. Authoring: lazy index creation + full-template
  scaffolds (CR0077), executable `init` (CR0079), batch create (CR0078), decisions log (CR0080),
  reconcile field projection (CR0082), greenfield runbook (CR0081). Implementation/conformance:
  the test-spec AC-to-test bridge (CR0085), the Definition-of-Done verify gate (CR0084), the
  cross-epic AC lint (CR0086), and agent-instructions that enforce the tool-first discipline
  (CR0083). Released in v3.0.1.
- **v3.0.1 - the `sprint` lifecycle (RFC0019 Accepted, CR0087-0093):** dogfood-built next.
  `autosprint` renamed to **`sprint`** (CR0087; deprecated alias kept). The command is now the
  whole sprint lifecycle via the **goal ladder** `triage -> plan -> design -> done` (cumulative
  stop-points; NL maps to the furthest rung). New: `--goal plan` sprint planning (CR0091);
  greenfield **authoring** from a PRD - `sprint <prd.md> --goal design` drives PRD -> epics ->
  stories with two STOPs (CR0088-0090); `design` assigns story points (CR0092); a closing
  consistency pass over the backlog (CR0093). The loop is documented in `reference-sprint.md`.
- **v3.0.1 - sprint-2 hygiene + hardening (CR0094-0099, Part A stories):** dogfood-run via
  the sprint lifecycle (plan -> breakdown -> run). The 5 stale v2.0 Ready stories (US0001-0005)
  verified-and-closed - the Done-gate (CR0084) blocked a false close on a stale verifier, proving
  the loop. New: reconcile-before-plan (CR0094); `quality.done_requires_verified` toggle + status
  verify lane (CR0095); hard epic-scope test-spec requirement `verify_ac epic-ts` (CR0096);
  persona index-projection via a canonical field (CR0097); the audit flags **already-satisfied**
  Ready units (CR0098); **seat-scored WSJF** sprint planning (CR0099). LL0007 captured the
  planning learnings. 855 tests, gate clean.
- **v3.0.1 release + RV0005 self-review (2026-06-24):** a full adversarial sweep (the audit
  skill-profile, 4 lenses) plus best-practice / progressive-disclosure / token-economy review.
  ~61 candidates -> refute panel -> 6 actionable survivors, all fixed before the tag (BG0034 the
  lowercase-status silent-empty-batch bug; CR0100 cascade re-anchored on `artifact.py close`;
  CR0101 reconcile help points at the script; CR0102 `--no-artifacts` de-duplicated to one anchor;
  CR0103 SOTA linters in the best-practice guides; CR0104 surfaced `decisions`/goal-ladder/`init`
  in the router; CR0105 id-allocation for review/retro). Verdict: **lean and coherent** - the
  always-loaded Type Reference and the baked language guides were assessed and *kept* (panel
  refuted their removal). Consolidated into **v3.0.1** (the `autosprint` -> `sprint` rename; alias
  preserved). Full record: `RV0005-skill-review-v3.md`.

## Operating reminders

- Trunk-based: small green commits to main, each gated on `npm run lint && npm test && gate`.
- Forward-port skill edits repo -> install targets via manual rsync (not `install.sh --local`).
- Stakes-scaled review (CR0061): full independent critic for code/risky units; lighter recorded
  review for pure-doc/mechanical ones.
