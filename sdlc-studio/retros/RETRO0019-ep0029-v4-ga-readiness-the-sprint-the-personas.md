# RETRO-0019: EP0029 v4 GA readiness: the sprint the personas ran

> **Date:** 2026-07-10
> **Batch:** EP0029 (9 units): 6 dogfood findings + 2 operator directives + 1 bug found mid-sprint
> **Goal:** done (close every finding and document the big-bang v4 before the GA tag)
> **Delivered:** 9 / 9   **Blocked:** 0

## Delivered

- **BG0101** - reconcile covers epic breakdown checkboxes for every unit type; scoped to the
  Story Breakdown section after the critic proved the first cut ticked Definition-of-Done items.
  The lane surfaced 21 real drifted boxes in EP0026/27, then caught its own epic's drift live at
  this close.
- **CR0216 + BG0102** - the numbering switch is an explicit operator question with THREE answers
  (full migration / forward-only `adopt` / decline), `apply`/`adopt` refuse without `--confirm`,
  an era-divergence advisory warns when a v2 clone meets v3 ids, and an upgrade can no longer
  stamp a migrated project's schema back down.
- **CR0213** - the one-call gated bug close (`set --depth --verdict --reviewer --author`); after
  the critic's repro, every statically predictable refusal happens before any write.
- **CR0214** - `install.sh --from` installs the local working tree; after the critic's repro, the
  sweep can never touch the source it is installing from (the BG0100 class, closed for good).
- **CR0212** - `eval_run.py`: the eval gate's deterministic spine, used the same day for this
  epic's own gate (run `2026-07-10-ep0029`, 8/8 PASS).
- **CR0215** - the big-bang v4 docs pass: the README leads with the multi-team story
  (collision-free identity, the three-answer upgrade question, living Cooper personas).
- **CR0217** - living personas made the explicit default for reviews/critics/consults.

## Blocked / deferred

- None.

## What went well

- **The personas ran the quality loop, and it visibly out-performed the previous sprint's.**
  Sam (QA seat) rejected wave 1 with three working repros - each a real defect the unit tests
  missed, one of them (the sweep clobbering the `--from` source) the exact data-loss class the
  unit existed to close. Lena (Product seat) verified every README claim against shipped
  behaviour and rejected a factually false sentence in INSTALL.md. Every finding was repaired
  test-first and re-verified by the same critic before any unit reached a terminal status.
- **The sprint's own deliverables were dogfooded within the sprint:** the one-call close closed
  this sprint's bugs, the breakdown lane synced this epic's own boxes, `eval_run` ran this
  epic's eval gate, and the retro you are reading was tool-created.
- **Mid-sprint operator steering absorbed cleanly:** forward-only adoption, the era-divergence
  warning, the README multi-team emphasis, and CR0217 all arrived as messages mid-run and were
  folded in as scope amendments with the CR paperwork updated (revision rows + AC additions).

## What was hard / what stalled

- **My unit tests kept validating the happy path the critic then broke.** All three REJECTs were
  cases my tests deliberately avoided (`--no-sweep` in every install test, breakdown fixtures
  that only contained breakdowns, no undershoot case in the one-call tests). The adversarial
  seat is not optional ceremony; it is where the real defects surfaced - twice now across two
  sprints.
- **Scope-tracking under live steering takes discipline:** two operator additions landed in the
  implementation before the CR's ACs said so; the gap was caught and repaired, but the honest
  order is amend-the-artefact-first.

## Lessons

- **A guard tested only with the guard disabled is untested.** Every install test passed
  `--no-sweep`, so the sweep's interaction with `--from` was invisible. Regression tests must
  encode the critic's exact repro, hostile flags included.
- **Scope a mechanical writer to the section that gives its edit meaning.** A checkbox means
  "unit delivered" only inside the Story Breakdown; the same syntax elsewhere means something
  else. Grep-shaped writers need structural scoping, not just pattern matches.
- **Seat-resolved reviews change the findings, not just the framing.** Lena's product lens
  caught a false installer claim and an over-claim ("provably") that a generic reviewer -
  including this author - read straight past. CR0217 makes that the default, permanently.

## Metrics

- Units: 9 / 9, 0 blocked · 13 commits · Tests: 1586 skill + 132 tools green · drift 0
  throughout · Critic rejects: 3 (all repaired test-first, all re-verified by the same seat) ·
  Eval gate: 8/8 PASS (run `2026-07-10-ep0029`, via the new `eval_run`).
