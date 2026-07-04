<!--
Sprint retro for the 2026-07-B sprint (sprint 2). Related: reference-sprint.md,
RFC0022, CR0134/EP0011, BG0047, BG0048, BG0049, RETRO0006.
-->
# RETRO-0007: Mutation-gate sprint (RFC0022 accepted and built)

> **Date:** 2026-07-04
> **Batch:** BG0047, BG0048, CR0134 (RFC0022 -> EP0011 / US0051-US0054) + emergent BG0049 + the operator-approved Fixed->Closed sweep + the RFC0018 pressure-test
> **Goal:** done
> **Delivered:** all planned units   **Blocked:** 0

## Delivered

- **RFC0022 Accepted** (operator decision, D0002) and **built to Done in the same sprint**:
  EP0011's four stories delivered the executable mutation-check gate - `mutation.py`
  (declared fault classes, per-language textual profiles, killed/survived/error/unviable
  verdicts, honest truncation and un-checked reporting), the advisory gate lane
  (absent = not-run, different-rev = STALE, never PASS), and the docs that turn the
  assertion-integrity prose into a pointer at enforcement.
- **BG0047**: seat-sized WSJF (`size` slot in wsjf-inputs; unknown effort never ranks minimal).
- **BG0048**: provenance remake honours `adopt_after`; any non-empty Created-by is provenance.
- **BG0049** (emergent, found authoring TS0002): ts-check's matrix parser bled into
  References/Revision History tables - same structural-boundary class as BG0046; fixed
  test-first, live-verified on both specs.
- **Sweep (D0003)**: the 44 historical Fixed bugs transitioned to Closed - a recorded
  convention normalisation, not fresh verification.
- **RFC0018 pressure-tested** against the current tree: recommendation accept-reduced
  (telemetry `show --summary` S; verb-taxonomy guidance S; decline the vocabulary checker -
  no repeat incident, constitution.md is its right home if one recurs). Operator decision open.

## The loop, observed

- **The critic loop ran twice and paid twice.** First pass: request-changes with a HIGH
  finding - non-compiling mutants counted as killed, so a vacuous suite could earn a clean
  report (6.2% of mutants over our own scripts). That is the exact false-evidence class the
  gate exists to catch, caught in the gate itself before first release. Seven findings, seven
  fixes seen RED first, re-verified against the critic's own repros, approved across all
  units; verdicts recorded author != reviewer. Lesson L-0002.
- **Dogfooded in-session** (operator directive): the gate ran twice over this sprint's own
  changed scripts (12 applied, 12 killed, 0 unviable, 2888 truncated honestly); the sprint was
  planned with the mixed-batch queries CR0138 shipped last sprint; the depth gate CR0136
  shipped last sprint governed this sprint's bug closures.
- **Design-rung emergent defect**: authoring the epic's test-spec at design surfaced BG0049
  before any implementation ran - the shift-left bridge finding a parser bug on day one.

## Known residuals (logged, not hidden)

- Mutation staleness is rev-granular: a same-rev report stays fresh across uncommitted edits
  (critic low; v2 candidate: compare target mtimes/dirty state).
- Docstring-shaped lines can false-survive (1/4108 here; triage note in help/mutation.md).
- CR0141 (operator-filed, Proposed): product_reconcile's feature-map parser inert against
  real PVD trace cells - next sprint's candidate. Name generalised per the neutrality guard.

## Actions

- [ ] Operator: decide RFC0018 (recommendation: accept-reduced).
- [ ] Backlog: CR0141 (product_reconcile parser) - Proposed, Medium.
- [ ] v2 candidates: mutation staleness beyond rev-granularity; JS/Go profile tests grew this
      sprint - extend when a consuming JS/Go project first uses the gate in anger.
- [ ] Consider promoting L-0001/L-0002 to the skill tier after one more project proves them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Sprint close retro |
