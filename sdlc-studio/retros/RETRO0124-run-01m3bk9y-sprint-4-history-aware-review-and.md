# RETRO-0124: RUN-01M3BK9Y Sprint 4: history-aware review and the review paperwork deleted

> **Date:** 2026-09-25
> **Batch:** BG0750, BG0751, BG0753, BG0756, BG0757, BG0758, BG0759, BG0760, BG0761, BG0762, BG0763, BG0764, BG0765, BG0766, BG0767, BG0768, BG0769, BG0770, US0910, US0911, US0912, US0913, US0916, US0917, US0920, US0921, US0927, US0928, US0929, US0930, US0931, US0932, US0933, US0934, US0935

## Keep

- Reading the record at the moment of work: every lane brief now carries the history of the files it touches (US0931), goals trace to a PRD outcome (US0927-US0929), and the PRD states its outcomes O1-O8. Reviewers cited prior art in their findings, and the only design question the run met (US0914's 35 historical units) was surfaced by a builder before any code landed.
- Deleting the review paperwork nobody reads: the plan review, test-plan gate and tooling, repair plan, two-role gate and per-unit sign-off, depth tiers, derived depth, evidence drift, the gate's mutation lane, the repair mutation gate and the plan-review phase are gone - 12 EP0263 stories, and thousands of lines of production and test code, with each retired criterion recorded in the D0259 pattern.
- One QA-seat reviewer per unit, capped at two rounds, and carrying at the cap: 14 units were rejected at round 1, 12 converged at round 2, and the two that did not (US0909, US0915) were carried as BG0767 and BG0769 and landed in the same run, so the cap cost a round rather than a sprint.

## Stop

- Turning main red with this sprint's own tests: BG0764, BG0766, BG0768 and BG0770 each fixed a test landed earlier in the run, and CI stayed red on tools/tests for an afternoon because the push gate runs pytest while CI runs unittest discover, so a module global shared across importers and an xdist-only probe passed locally.
- Building deletion units in parallel against a moving base: US0909, US0935, US0917 and US0912 each had to be rebased onto sibling deletions, and two of the rebases (a surface verb count taken by hand, a criterion edited by both sides) produced findings of their own.

## Try

- [LC-002] Cited again as the dominant REJECT class: tests rewritten with their names kept while a stamped criterion still claimed the deleted behaviour (US0915 on four stamps, US0912 on BG0553). When a deletion trims a stamped test, re-read the stamping criterion's words, not only the selector.
- [LC-008] US0914's build showed that deleting a ledger can silently strip a derived status from 35 historical units, and the obvious answer, a waiver each, is the paperwork being deleted. Before a deletion lands, run whole-workspace conformance with it applied and rule the historical answer as a criterion.
- [new: the push gate and CI disagree on the runner | build] A test is green only under the runner CI uses. Before pushing a new test module, run it under `python3 -m unittest` as well as pytest, and prefer one runner at push and in CI (BG0770).
