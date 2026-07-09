# LATEST - current project state (v4.0.0-rc.1 prepared; not yet tagged/pushed)

> The current-state anchor - a WINDOW, not a ledger. **Re-read this and run
> `/sdlc-studio status` after any context reset or compaction.** Durable guidance lives in
> AGENTS.md; per-sprint detail lives in the retros and CHANGELOG.md; keep this file under
> `docs.latest_max_lines` (doc-freshness advisory) by moving past sprints to History lines.
>
> **Version:** `4.0.0-rc.1` prepared (the maturity release: schema v3 active + default for new
> projects) · **Date:** 2026-07-09 ·
> **Gates:** 1455 + 108 tests pass, `gate` PASS, reconcile drift 0, `npm run lint` green
> (BG0075 fixed; commit hook now enabled in this clone).
>
> **rc-tag / push is operator-gated.** The version strings and CHANGELOG are homed at `4.0.0-rc.1`
> and the pre-v4 dormant/freeze banners are removed, but the actual `git tag v4.0.0-rc.1`, the
> freeze lift, and the push to consuming projects remain an explicit operator action once the
> rc-readiness checklist (`sdlc-studio/reviews/v4-rc-readiness.md`) reads green. `main` runs ahead
> of `origin` until then.

## Current

- **RV0007 REPOSITORY REVIEW (2026-07-09): 42 verified findings, 9 rc-BLOCKERS - hold the v4.0
  tag.** Five-leg deep review (code, architecture, reliability, test/CI, defensive security) at
  the rc; every finding re-verified, most reproduced. Filed BG0071-BG0096 (6 High, 20 Medium),
  CR0202-CR0208, and RFC0027 (world-class roadmap; recommendation: blocker fix pack -> tag ->
  three themed epics). Blockers: BG0071 (reconcile apply KeyError on dated indexes), BG0072
  (close cannot type ULIDs), BG0073/74 (interrupted migration cross-wires ids; walk never stamps
  schema 3), BG0075 (lint red at HEAD; commit hook never enabled, CI dark), BG0077/78 (filer not
  era-aware; consolidation false-failure), BG0079/80 (eval gate missing from the rc checklist;
  superseded-regime docs). Backlog is deliberately NO LONGER EMPTY. See
  `RV0007-repository-review-2026-07-09-code-architecture-reliability.md`.
- **EP0024 + EP0025 DELIVERED - v4.0.0-rc.1 PREPARED (2026-07-09).** v4 release engineering +
  backlog clearance: 8 units + BG0070 fix, both epics Done; committed to `main` (unpushed). US0105
  `init` defaults new projects to `schema_version: 3` (existing untouched, override-only reader);
  US0106 rehearsed the v2->v3 upgrade walk on two real projects (found+fixed BG0070, a per-file
  `git log --follow` scale defect); US0107 majors-only release-gate section; US0108 version ->
  `4.0.0-rc.1` + banners removed; US0109 rc-readiness checklist; US0110 `status.py backlog` census;
  US0111 provenance guard widened; US0112 closed BG0067-0070, archived indexes, `validate` accepts
  v3 ULID. Closes CR0198/CR0199/CR0201. 1457 tests, gate PASS, drift 0. The closing full-diff critic
  caught a cross-unit schema-source split (a fresh v3 project shown a v2->v3 walk) - fixed before the
  rc. See RETRO0016. **rc tag / freeze lift / push are OPERATOR-GATED** (see `v4-rc-readiness.md`):
  the checklist reads green; the tag decision is yours.
- **Backlog now: EMPTY.** No non-terminal artefacts across every type. The 9 founding epics
  (EP0001-0009) that carried a stale `Ready` are all closed to Done - their capabilities ship in
  v4.0.0-rc.1 (each carries a "founding epic" note; unlinked `US:` breakdown items are early
  placeholder stubs, complete in the implementation).
- **Deferred follow-ups (open ideas, unfiled):** a `reconcile detect --era` lens + per-artifact
  re-review markers + per-capability watermarks (CR0197 open decisions); a path-aware tightening of
  the spec-guard basename match; the 6 legacy-epic stale-`Ready` hygiene pass above.
- **Benchmark evidence base (N=5, `2026-07-08-n5-run.md`):** unstructured arms escaped 10/10 on
  notify-digest vs mandated-planning 2/5 (Fisher p 0.083); Auditability tracked escapes (R 0.88 >
  A 0.68 > B 0.60); routing 0.40 cost index, ~3.1x baseline tokens. Failure mode "a bad plan
  propagates" -> CR0194. Positioning docs cite these numbers.

## History (detail lives in the named retro / CHANGELOG entry)

- **EP0022 + EP0023 RV0006 debt + context tiering (2026-07-09)** supply-chain SHA pins + installer checksum, sync/verifier hardening, shared-layer consolidation, complexity-hotspot decomposition, context-tiering digests; closes CR0186/CR0187/CR0179 -> RETRO0015

- **EP0020 + EP0021 clear-the-decks (2026-07-09)** upgrade re-baseline, `reference-scripts` split, shared discovery, archive consolidation, origin-drift pre-flight; BG0068/BG0069; closes CR0197/0200/0181/0182/0188 -> RETRO0014
- **EP0019 plan-integrity hardening (2026-07-09, schema-v3 dormant)** deterministic plan-review gate (AC-vs-spec, fingerprint-pinned), reviewer charter + telemetry, spec-edit guard, bench phase field; closes CR0194/0195/0196 -> RETRO0013
- **EP0014 agentic triage (2026-07-09, schema-v3 dormant)** inbox->triaged vocab + gated transition, noise controls (session cap, Low consolidation), record-only Tranche, sampled-audit metrics; closes CR0173/CR0172 -> RETRO0012
- **v4 Tranche 2 (WIP, unreleased)** authorship & enforcement (EP0013) + tooling debt (EP0018, several CRs scoped forward) + benchmark protocol; 13 stories, era-gated -> CHANGELOG
- **v4 foundation (WIP, unreleased)** distributed artefact identity, schema v3 (EP0012/EP0015): ULIDs, `migrate_v3.py`, GitHub aliases, atomic writes; RFC0024/0025; preceded by RV0006 (14 bugs) -> CHANGELOG
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
