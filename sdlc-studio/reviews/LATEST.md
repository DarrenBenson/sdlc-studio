# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXS5JY** (the close-chain robustness
> sprint, 2026-07-18, RETRO0048). Supersedes the RETRO0047 picture.

## Where the pipeline is (2026-07-18)

The **close-chain robustness sprint** (RUN-01KXS5JY) is delivered: **7/7 units, Sprint Goal
ACHIEVED**. The batch was the close/gate/sprint-tooling family from the 2026-07-16 audit triage:
two follow-up bugs and two epics.

- **BG0188 (High):** `open_run` now treats a run carrying any close artefact (`sprint_goal_verdict`
  / `ended_at` / `handoff`) but `outcome=running` as spent and mints a fresh run - closing the
  hazard where `sprint plan --write` accumulated a new batch onto a judged run and clobbered its
  verdict. A clean running run still accumulates.
- **BG0189 (Low):** `project_upgrade.CURRENT_SCHEMA` derives from the single source of truth
  (`templates/config.yaml` via new `sdlc_md.current_schema()`); the `.version` stamp and `audit()`'s
  `stale-version` finding follow the project's own effective/config schema, so a legitimately-v2
  project is neither silently advanced nor left with a permanent false finding.
- **EP0077 (US0236/US0237/US0238):** `sprint close --apply-signoff --principal "<you>"` fans a
  recorded operator approval into per-unit sign-offs + Done transitions, then a tail that writes the
  run's velocity row and a final reconcile. Story-scoped, idempotent, stops loud at the first refusal.
- **EP0080 (US0247/US0248):** a recorded sprint-level adversarial full-diff verdict
  (`critic sprint-review`) satisfies the per-unit `critiqued` gate as coverage for the units in its
  range (never overriding a per-unit REJECT; sign-off still per unit), and the close sign-off brief
  reads a covered unit as reviewed rather than unreviewed.

## CODE leg

The close CODE leg was ONE independent adversarial full-diff review over `e53202a..HEAD` (refute
framing, a repro per claim), recorded as a sprint-level verdict - dogfooding EP0080. **Round 1
REJECT (BLOCKING):** the review reproduced a regression BG0189 introduced - `audit()` advertised a
`stale-version` auto-fix (`< CURRENT_SCHEMA`) that `apply()` no longer performs, leaving a v2
project a permanent uncorrectable finding. It also found the US0247/US0236 composition gap
(`_signoff_author` did not read the sprint-level review) and a two-role independence observation.
**Repaired** in commit 39f346a (audit/apply consistency + a v2-stamp regression test; author
resolved from the sprint review; principal refused when it equals the sprint reviewer), then
**re-verified** by the same reviewer. The independent review earned its cost: it caught a shipped
regression the author's own tests missed. Full suite 2858 green, drift 0, every commit gated.

## Document legs

`reference-sprint.md` (the sprint-level coverage model), `help/sprint.md` (`--apply-signoff`),
`CHANGELOG.md`, and the five groomed stories are the surfaces this sprint touched; each is
consistent with the shipped code and enforced by the gate.

## Next steps

- The five EP0077/EP0080 stories reach Done at this run's own close via `--apply-signoff` (dogfood):
  the sprint-level review is the evidence, the operator sign-off is the reviewer of record.
- Standing: **CR0278** (interactive-sprint token capture) - per-unit token actuals were not captured
  this run, so est/actual is uncomputable; the sprint total can be supplied with `accuracy --tokens`.
- Residual audit CRs (CR0280-CR0306) and BG0187 remain for a future scheduled batch.
- Release freeze holds until ~2026-07-21; everything lands unreleased on `main`.
