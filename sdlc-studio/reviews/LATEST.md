# LATEST - current project state (v3.6.0 released; v4 is WIP)

> The current-state anchor - a WINDOW, not a ledger. **Re-read this and run
> `/sdlc-studio status` after any context reset or compaction.** Durable guidance lives in
> AGENTS.md; per-sprint detail lives in the retros and CHANGELOG.md; keep this file under
> `docs.latest_max_lines` (doc-freshness advisory) by moving past sprints to History lines.
>
> **Released version:** 3.6.0 (2026-07-06, non-breaking - the EP0016 review/lite on-ramp) ·
> **Date:** 2026-07-06 ·
> **Gates:** lint clean, 1249 script tests pass (+49 repo-only tools tests), `gate` PASS,
> reconcile drift 0, npm audit 0, CI green on main.
>
> **Fixed:** `verify_ac.py`'s `pytest <path> -k <marker>` DSL glued the tail into one argv
> element (false "file not found"); now `shlex.split`, matching the `go` verb.
>
> **v4 is WORK-IN-PROGRESS, not released.** The v4 foundation (schema-v3 ULID identity - a
> breaking change) and Tranche 2 (authorship/enforcement + tooling debt) are all on `main` and
> ship **dormant** in v3.6.0: opt-in via `schema_version: 3` (defaults to 2), so v3.6.0 stays
> non-breaking and nothing renumbers. v4.0 is cut only once the backlog is complete AND it has
> been tested in anger on real projects.

## Current

- **v3.6.0 RELEASED - review/lite on-ramp (EP0016, non-breaking).** Two try-before-you-adopt
  entry points, trunk-based to main, RED-first. US0070 `review generate`: a zero-setup host-repo
  review (`review_generate.py` owns bootstrap + the verbatim remediation-only security policy +
  the secret-absence scan; the review itself runs from `templates/workflows/repo-review.md`).
  US0071 lite profile: `profile: lite` collapses the pipeline to PRD -> story -> implement (no
  epic layer, no nag), promotable to full via `lite_profile.py promote`. Both non-breaking and
  independent of the dormant schema-v3 work. Tagged v3.6.0.
- **v4.1.0 - authorship & enforcement (EP0013) + tooling debt (EP0018) + benchmark protocol.**
  13 stories, trunk-based to main. EP0013: structured typed authorship (US0060, resolver +
  backfill), separation-of-duties lint (US0061), evidence-as-schema (US0062), the consolidated
  `audit_check.py` (US0063), and the cross-script invariant tier (US0064 - which caught a
  BG0053 regression). EP0018: config warn-once (US0076), shared discovery (US0077), archive
  correctness guard (US0078), state-hygiene (US0079), reconcile docstring + apply JSON (US0080),
  batch-wiring guard (US0081), `digest.py` context tiering (US0082). Plus US0073 (pre-registered
  benchmark protocol). All schema-v3 enforcement is era-gated; v2 projects untouched. Several
  EP0018 CRs delivered a slice with the larger refactor scoped forward (CR0181/0182/0186/0187).
- **v4.0.0 - distributed artefact identity (schema v3), the team-tool foundation.** The 6-story
  foundation sprint (EP0012 identity + EP0015 concurrency), delivered trunk-based to main:
  US0055 ULID generator + era-tolerant readers, US0056 v2->v3 migration (`migrate_v3.py`, order-
  preserving, aliased, idempotent), US0057 friendly GitHub aliases, US0058 `index-derived` gate
  check, US0069 atomic writes + advisory lock, US0059 TRD refresh + freshness guard. All opt-in
  via `schema_version: 3`; v2 projects untouched. RFC0024 + RFC0025 accepted. Preceded by the
  RV0006 self-review bug sweep (14 bugs, BG0053-BG0066) and the v4 breakdown (22 CRs into 7
  epics and 28 stories).
- **Backlog swept (2026-07-08):** EP0012/13/15/18 + 13 CRs were fully story-Done but stuck at
  Draft/Proposed (status never cascaded) - closed mechanically, 0 drift after. Real remaining
  backlog: **EP0014** agentic triage (US0065-0068), **EP0017** positioning/benchmark
  (US0072/0074/0075), 5 EP0018 debt CRs not yet decomposed (CR0179/0181/0182/0186/0187), plus
  CR0188 (fetch-before-sprint).
- **Next:** before a v4 "big bang" cut, run the RFC0025 N=1 benchmark spike early - nothing has
  validated the v4 premise beyond unit tests. Then EP0014 or EP0017. Migrate via
  `migrate_v3.py apply` when chosen (still v2).

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
