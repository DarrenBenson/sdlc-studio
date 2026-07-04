<!--
Sprint retro for the 2026-07 mixed backlog-clear tranche. Related: reference-sprint.md,
BG0045, BG0046, CR0132, CR0133, CR0135, CR0136, CR0138, RFC0022.
-->
# RETRO-0006: Mixed backlog-clear sprint (field-report tranche)

> **Date:** 2026-07-04
> **Batch:** BG0045, BG0046, CR0132 (absorbing CR0139), CR0133, CR0135, CR0136, CR0138, CR0134 (RFC-first)
> **Goal:** done
> **Delivered:** 7 / 8 units   **Blocked:** 1 (CR0134, by design - awaits the RFC0022 decision)

## Delivered

- **BG0045 + BG0046 - the lying-gate pair.** The bug-readiness check accepts the shipped
  template's own headings (rendered-template regression per the gate-validated-against-its-own-
  template discipline), and the duplicate-id table boundary is structural, not vocabulary-based.
- **CR0132 (+CR0139) - self-diagnosing findings.** count-mismatch names the status tokens, both
  numbers, the out-of-vocab carriers and the `status_vocab` remedy; validate names the config
  extension mechanism. The fixture reproduces the field dead-end and the config declaration
  clears it.
- **CR0133 - the toolbox is discoverable.** Deterministic Entry Points card in the router,
  task-to-script rows in the loading guide, doctrine rule 15, non-interactive create as the
  canonical path in agent-instructions and help.
- **CR0136 - depth tiers enforced.** transition refuses Fixed below functional and
  production-affecting Closed below soak; missing depth is refused, never assumed; story
  depth-parity advisory, config-gateable.
- **CR0138 - mixed tranches first-class.** Combinable queries, a real worklist input, one
  cross-type weight scale, sequenced-in-batch audit reclassification, conformance scoping
  stated. Live-verified against this very sprint's plan.
- **CR0135 - British spelling checked, not stated.** Bounded list, allowlisted identifiers,
  scan-root argument for fixture tests; the guard caught this sprint's own changelog wording.
- **CR0134 -> RFC0022.** Epic-sized with unsettled design, so the sprint delivered the RFC
  (4 options, recommendation, open decisions D1-D6); the CR is Blocked pending the decision.

## The loop, observed

- **The independent critic earned its place.** Post-delivery adversarial review returned
  request-changes with one high finding: the BG0046 fix had not swept the sibling parsers, so
  the closed bug's field outcome was still reproducible - plus an LL0008 loop (apply reporting
  a change it did not make). Six findings, six fixes, each seen RED first; the critic re-ran
  the original repros and approved. Author != reviewer caught what the author's own green
  tests could not. Lesson recorded (L-0001).
- **Dogfood catches filed deterministically:** BG0047 (WSJF size seed ranks new-file units
  trivially small; no seat effort slot) and BG0048 (provenance remake ignores the adopt_after
  cutoff and double-stamps a non-tool Created-by).
- **Estimates:** Engineering's seat sizes (2/2/3/5/5/8/3/13) tracked effort well; the
  deterministic complexity seed inverted the order (BG0047). Seat-scored WSJF with hand-held
  sizes produced the executed sequence.

## Actions

- [ ] Operator: decide RFC0022 (D1-D6); on acceptance decompose CR0134 into an epic.
- [ ] Backlog: BG0047 (WSJF sizing), BG0048 (provenance remake) - both Open, neither urgent.
- [ ] Consider promoting L-0001 to the skill tier once it proves out in another project.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Sprint close retro |
