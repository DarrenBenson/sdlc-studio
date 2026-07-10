# LATEST - current project state (v4.0 ready; not yet tagged/pushed)

> The current-state anchor - a WINDOW, not a ledger. **Re-read this and run
> `/sdlc-studio status` after any context reset or compaction.** Durable guidance lives in
> AGENTS.md; per-sprint detail lives in the retros and CHANGELOG.md; keep this file under
> `docs.latest_max_lines` (doc-freshness advisory) by moving past sprints to History lines.
>
> **Version:** `4.0.0-rc.1` prepared (the maturity release: schema v3 active + default for new
> projects) · **Date:** 2026-07-10 ·
> **Gates:** 1562 skill + 117 tools tests pass, `gate` PASS, reconcile drift 0, `npm run lint` green.
>
> **rc-tag / push is operator-gated.** The version strings and CHANGELOG are homed at `4.0.0-rc.1`
> and the pre-v4 dormant/freeze banners are removed, but the actual `git tag v4.0.0-rc.1`, the
> freeze lift, and the push to consuming projects remain an explicit operator action once the
> rc-readiness checklist (`sdlc-studio/reviews/v4-rc-readiness.md`) reads green. `main` runs ahead
> of `origin` until then.

## Current

- **RV0007 ROADMAP DELIVERED - THE WHOLE BACKLOG IS CLEAR (2026-07-10).** RFC0027 option C, all
  three epics Done: **EP0026** gate integrity (10, the meta-layer verifies itself; evals 4/4;
  caught BG0099), **EP0027** reliability tier (11, crash-safe/resumable/honest-under-failure),
  **EP0028** era completion + DX (9: BG0086/87/88/93/97/99 make schema-v3 behave end-to-end, plus
  CR0211 retros/reviews reconciled, CR0210 one CLI grammar, CR0208 a 10-AC quality/docs sweep -
  fenced-block-safe parsers, cmd_plan/cmd_push decomposed 73/85 -> 10/9). Every unit critic-approved;
  the CR0208 closing critic traced the decompositions line-by-line; eval 2/2 on the new v4 scenarios
  (05 schema-v3 identity, 06 independence gate). See RETRO0018.
- **Backlog now: EMPTY.** No non-terminal artefacts across every type - this is the precondition the
  operator set for the v4.0 tag. RFC0027 accepted (option C); the 9 founding epics (EP0001-0009) that
  carried a stale `Ready` remain closed to Done. **The tag / freeze lift / push to consuming projects
  stay an explicit operator action** (see `v4-rc-readiness.md`); `main` runs ahead of `origin`.
- **RV0007 (2026-07-09):** five-leg repository review, 42 verified findings -> BG0071-BG0099,
  CR0202-CR0211, RFC0027. Preceded by the nine-rc-blocker fix pack (RETRO0017) and EP0024/EP0025
  v4 release engineering (RETRO0016). All now delivered.
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
