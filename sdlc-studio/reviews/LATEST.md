# LATEST - current project state (v4.0.0)

> The current-state anchor - a WINDOW, not a ledger. **Re-read this and run
> `/sdlc-studio status` after any context reset or compaction.** Durable guidance lives in
> AGENTS.md; per-sprint detail lives in the retros and CHANGELOG.md; keep this file under
> `docs.latest_max_lines` (doc-freshness advisory) by moving past sprints to History lines.
>
> **Project version:** 4.0.0 (released 2026-07-06) ·
> **Date:** 2026-07-06 ·
> **Gates:** lint clean, 1200 script tests pass (+46 repo-only tools tests), `gate` PASS,
> reconcile drift 0, disclosure 1 (advisory), npm audit 0, CI green on main.

## Current

- **v4.0.0 - distributed artefact identity (schema v3), the team-tool foundation.** The 6-story
  foundation sprint (EP0012 identity + EP0015 concurrency), delivered trunk-based to main:
  US0055 ULID generator + era-tolerant readers, US0056 v2->v3 migration (`migrate_v3.py`, order-
  preserving, aliased, idempotent), US0057 friendly GitHub aliases, US0058 `index-derived` gate
  check, US0069 atomic writes + advisory lock, US0059 TRD refresh + freshness guard. All opt-in
  via `schema_version: 3`; v2 projects untouched. RFC0024 + RFC0025 accepted. Preceded by the
  RV0006 self-review bug sweep (14 bugs, BG0053-BG0066) and the v4 breakdown (22 CRs into 7
  epics and 28 stories).
- **Open backlog:** the rest of the v4 tranches - EP0013 (authorship/enforcement), EP0014
  (agentic triage), EP0016 (review/lite on-ramp), EP0017 (positioning/benchmark), EP0018
  (tooling debt). 21 CRs still Proposed.
- **Next:** groom EP0013's stories to Ready and run the enforcement tranche; consider the RFC0025
  N=1 benchmark spike early (validates the v4 premise). The dogfood repo can migrate to schema v3
  via `migrate_v3.py apply` when chosen (currently still v2, capability shipped).

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
