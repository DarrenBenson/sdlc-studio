# LATEST - current project state (v3.4.0 + two unreleased tranches on main)

> The current-state anchor - a WINDOW, not a ledger. **Re-read this and run
> `/sdlc-studio status` after any context reset or compaction.** Durable guidance lives in
> AGENTS.md; per-sprint detail lives in the retros and CHANGELOG.md; keep this file under
> `docs.latest_max_lines` (doc-freshness advisory) by moving past sprints to History lines.
>
> **Project version:** 3.4.0 (released 2026-07-04) + unreleased tranches - v3.5.0 pending ·
> **Date:** 2026-07-05 ·
> **Gates:** lint clean, 1162 script tests pass (+41 repo-only tools tests), `gate` PASS,
> reconcile drift 0, disclosure 0, npm audit 0, CI green on main.

## Current

- **Sprint 2026-07-D - field-hardening (unreleased, RETRO0010):** 8/8 CRs delivered, sourced
  from a consuming project's first-day field reports. RFC0023 accepted (D0010) and built as
  `lib/conventions.py` - the tolerant convention layer (status-column aliases, companion
  suffixes, bug-ready section vocabularies, scaffold template overrides; config-declared,
  fail-loud, byte-identical unconfigured); CR0154/0155 adopt it. Plus: one degenerate-index
  diagnostic with refusing apply (CR0153), mutation sampling disclosure (CR0152), `Verified` =
  gated higher-tier proof (CR0156), seat-score provenance (CR0151), `project upgrade`
  capability digest + advisory-lane registry (CR0157). Critic: 9 findings (2 HIGH), all fixed,
  repros re-run -> APPROVE; lesson L-0005 (census-consumer sweep). CR0159 (apply inserts
  missing summary rows, fail-loud residuals) delivered as an addendum.
- **Token-optimisation tranche (in flight, CR0160-CR0163):** index-bloat advisory + first live
  archive run (265 rows -> `archive/v3.4.0/`, live indexes 332 -> 83 lines), LATEST.md
  window discipline (this rewrite), `artifact.py revision` verb, slice-read rule.
- **Open backlog:** none beyond the in-flight tranche.
- **Next:** release v3.5.0 (evals, tag, deploy); consuming projects then upgrade and get the
  first live CR0157 capability digest.

## History (detail lives in the named retro / CHANGELOG entry)

- **2026-07-D** field-hardening: convention layer + adoption onboarding -> RETRO0010
- **D0006** first instrumented sprint: telemetry-on-close, workspace advisory, BG0051 -> RETRO0009
- **2026-07-C** the re-scoped seven: iter_tables, mutation v2, batch transitions -> RETRO0008
- **2026-07-B** the mutation gate (RFC0022 -> EP0011), 44-bug sweep, WSJF sizing -> RETRO0007
- **2026-07** mixed backlog clear: first seat-scored WSJF sprint, depth tiers -> RETRO0006
- **EP0010** token economy + learning loop: index archival, retro gate, blocker sweep -> RETRO0005
- **CR0128** test-strategy heuristics follow-on (missing-regression-test audit lane)
- **v3.1.1** field-hardening from 4 upgrade-run retrospectives (RFC0021 seats/amigos) -> CHANGELOG
- **v3.1.0** your personal engineering team (RFC0020 amigos + independence gate) -> CHANGELOG
- **v3.0.1** consolidated v3 line: sprint lifecycle (RFC0019), greenfield DevEx CR0077-0086,
  hygiene sprint CR0094-0099, RV0005 self-review -> `RV0005-skill-review-v3.md`, CHANGELOG
- **v2.1-v2.4** autosprint + control plane; version check; PVD/provenance/gate/personas;
  project upgrade + deploy last-mile + neutrality guard -> CHANGELOG

## Operating reminders

- Trunk-based: small green commits to main, each gated on `npm run lint && npm test && gate`.
- Forward-port skill edits repo -> install targets via manual rsync (not `install.sh --local`).
- Stakes-scaled review (CR0061): full independent critic for code/risky units; lighter recorded
  review for pure-doc/mechanical ones.
- Consuming projects only receive features when a release is TAGGED - a fat [Unreleased]
  changelog is a standing prompt to propose one.
