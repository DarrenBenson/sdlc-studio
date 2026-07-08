# LATEST - current project state (v3.6.0 released; v4 is WIP)

> The current-state anchor - a WINDOW, not a ledger. **Re-read this and run
> `/sdlc-studio status` after any context reset or compaction.** Durable guidance lives in
> AGENTS.md; per-sprint detail lives in the retros and CHANGELOG.md; keep this file under
> `docs.latest_max_lines` (doc-freshness advisory) by moving past sprints to History lines.
>
> **Released version:** 3.6.0 (2026-07-06, non-breaking - the EP0016 review/lite on-ramp) ·
> **Date:** 2026-07-06 ·
> **Gates:** lint clean, 1274 script tests pass (+49 repo-only tools tests), `gate` PASS,
> reconcile drift 0, npm audit 0, CI green on main.
>
> **v4 is WORK-IN-PROGRESS, not released.** The v4 foundation (schema-v3 ULID identity - a
> breaking change) and Tranche 2 (authorship/enforcement + tooling debt) are all on `main` and
> ship **dormant** in v3.6.0: opt-in via `schema_version: 3` (defaults to 2), so v3.6.0 stays
> non-breaking and nothing renumbers. v4.0 is cut only once the backlog is complete AND it has
> been tested in anger on real projects.

## Current

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
  foundation sprint (EP0012 identity + EP0015 concurrency): US0055 ULID generator, US0056
  v2->v3 migration (`migrate_v3.py`, order-preserving, aliased, idempotent), US0057 GitHub
  aliases, US0058 `index-derived` gate, US0069 atomic writes + lock, US0059 TRD refresh. Opt-in
  via `schema_version: 3`; v2 untouched. RFC0024 + RFC0025 accepted. Preceded by RV0006 (14
  bugs, BG0053-BG0066) and the v4 breakdown (22 CRs into 7 epics, 28 stories).
- **Benchmark v2 complete through the measured N=5 run** (RFC0026 + CR0189-0193 Done;
  D0012 -> D0013 -> D0014). Model-tier routing shipped (`route.py`, advisory, tool-neutral);
  two harder Tier-1 fixtures + held-back Auditability metric, protocol-v2 pre-registered.
  **N=5 result (`2026-07-08-n5-run.md`): unstructured arms escaped 10/10 on notify-digest
  vs the mandated-planning arm's 2/5** (Fisher p 0.083, below significance); Auditability
  tracked the escapes exactly (R 0.88 > A 0.68 > B 0.60); routing cut delivery cost to a
  0.40 index on the easy fixture with zero escapes; routed pipeline ~3.1x baseline tokens
  per ticket. **New failure mode documented: a bad plan propagates** - 2/5 R planners
  mis-pinned SPEC R5 and the critic approved against the wrong oracle; in one of the two
  the worker wrote the error into the workspace spec itself. Points at an independent
  AC-vs-spec check before implementation.
- **US0072 delivered (CR0177, EP0017 now Done):** README reframed under the three hard
  constraints + the full progressively-disclosed value document (`docs/why-sdlc-studio.md`:
  thesis, labelled field results, benchmark evidence incl. the unflattering findings,
  economics, calibrated team-shape) + agent-facing discoverability (`llms.txt`, a For-agents
  README block, SKILL.md NOT-for triggers + openclaw metadata). Claims-calibration critic:
  REJECT->repair->APPROVE.
- **Next:** EP0014 agentic triage (US0065-0068), 5 EP0018 debt CRs
  (CR0179/0181/0182/0186/0187), CR0188; N=5 follow-ups filed: CR0194 (plan-stage
  AC-vs-spec adversarial review, deterministic trigger), CR0195 (unrequested spec edits
  block), CR0196 (bench summary calibration-row guard), BG0068 (supersedes status flip).

## History (detail lives in the named retro / CHANGELOG entry)

- **v3.6.0** review/lite on-ramp (EP0016): `review generate` zero-setup review + `profile: lite` -> CHANGELOG
- **BG0067** verify_ac pytest -k DSL glued path+marker (false file-not-found) - fixed, shlex.split
- **2026-07-08** backlog sweep: EP0012/13/15/18 + 13 story-Done CRs closed mechanically, 0 drift
- **2026-07-D** field-hardening: convention layer + adoption onboarding -> RETRO0010
- **D0006** first instrumented sprint: telemetry-on-close, workspace advisory, BG0051 -> RETRO0009
- **2026-07-C** the re-scoped seven: iter_tables, mutation v2, batch transitions -> RETRO0008
- **2026-07-B** the mutation gate (RFC0022 -> EP0011), 44-bug sweep, WSJF sizing -> RETRO0007
- **2026-07** mixed backlog clear: first seat-scored WSJF sprint, depth tiers -> RETRO0006
- **EP0010** token economy + learning loop: index archival, retro gate, blocker sweep -> RETRO0005
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
