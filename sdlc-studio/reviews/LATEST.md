# LATEST - current project state (v3.6.0 released; v4 is WIP)

> The current-state anchor - a WINDOW, not a ledger. **Re-read this and run
> `/sdlc-studio status` after any context reset or compaction.** Durable guidance lives in
> AGENTS.md; per-sprint detail lives in the retros and CHANGELOG.md; keep this file under
> `docs.latest_max_lines` (doc-freshness advisory) by moving past sprints to History lines.
>
> **Released version:** 3.6.0 (2026-07-06, non-breaking - the EP0016 review/lite on-ramp) ·
> **Date:** 2026-07-08 ·
> **Gates:** lint clean, 1274 script tests pass (+49 repo-only tools tests), `gate` PASS,
> reconcile drift 0, npm audit 0, CI green on main.
>
> **v4 is WORK-IN-PROGRESS, not released.** The v4 foundation (schema-v3 ULID identity - a
> breaking change) and Tranche 2 (authorship/enforcement + tooling debt) are all on `main` and
> ship **dormant** in v3.6.0: opt-in via `schema_version: 3` (defaults to 2), so v3.6.0 stays
> non-breaking and nothing renumbers. v4.0 is cut only once the backlog is complete AND it has
> been tested in anger on real projects.
>
> **Release freeze until v4.0 (operator directive 2026-07-08):** nothing releases to consuming
> projects before the v4.0 tag - all new v4-line work accumulates on `main` era-gated behind
> `schema_version: 3`. Commits land locally; the push/release waits for v4. `main` runs ahead
> of `origin` by design during the freeze.

## Current

- **Active sprint - EP0014 agentic triage, groomed to Ready (D0015).** US0065-0068 all Ready,
  era-gated behind `schema_version: 3`; findings-only prepend-`inbox` vocab (`inbox -> triaged`
  on CR/bug/RFC, stories/epics unchanged), sampling defaults (0.20 non-Critical + always
  Critical/disagreement), noise controls (session_cap 20, Low consolidation). Wave 1 US0065
  (vocab + gated-transition spine) -> Wave 2 US0066/0067/0068 parallel. Run
  `/sdlc-studio sprint --epic EP0014 --goal done`. Closes CR0173 + CR0172.
- **Backlog after EP0014:** 5 EP0018 debt CRs (CR0179/0181/0182/0186/0187), CR0188; N=5
  follow-ups CR0194 (plan-stage AC-vs-spec adversarial review), CR0195 (unrequested spec-edit
  block), CR0196 (bench calibration-row guard), CR0197 (upgrade re-baseline); v4.0 release
  engineering CR0198/CR0199; BG0068 (supersedes flip), BG0069 (install-path test).
- **Benchmark evidence base (N=5, `2026-07-08-n5-run.md`):** unstructured arms escaped 10/10 on
  notify-digest vs mandated-planning 2/5 (Fisher p 0.083); Auditability tracked escapes (R 0.88 >
  A 0.68 > B 0.60); routing 0.40 cost index, ~3.1x baseline tokens. Failure mode "a bad plan
  propagates" -> CR0194. Positioning docs cite these numbers.

## History (detail lives in the named retro / CHANGELOG entry)

- **v4.1.0 (WIP)** authorship & enforcement (EP0013) + tooling debt (EP0018, several CRs scoped forward) + benchmark protocol; 13 stories, era-gated -> CHANGELOG
- **v4.0.0 (WIP)** distributed artefact identity, schema v3 (EP0012/EP0015): ULIDs, `migrate_v3.py`, GitHub aliases, atomic writes; RFC0024/0025; preceded by RV0006 (14 bugs) -> CHANGELOG
- **US0072/EP0017** README reframe + `docs/why-sdlc-studio.md` value doc + agent discoverability (`llms.txt`, SKILL.md triggers) -> CHANGELOG
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
