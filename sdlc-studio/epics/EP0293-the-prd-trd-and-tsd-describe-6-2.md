# EP0293: The PRD, TRD and TSD describe 6.2, and the freshness census checks all three

> **Status:** Draft
> **Parent:** CR0647
> **Parent:** CR0646
> **Parent:** CR0645
> **Derived Point Total:** 27
> **Parent:** CR0649
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** S

## Summary

Decomposed from CR0649. Delivers the work CR0649 requested.

## Story Breakdown

- [x] [US1098: doc_freshness reports a count or version in the PRD or TSD that no longer matches the tree, as it does for the TRD](../stories/US1098-doc-freshness-reports-a-count-or-version-in.md)
- [x] [US1099: The TRD and the two stale code comments name sdlc_md.EXECUTES_VERIFIERS: stories and bugs execute their Verify lines, and CRs and RFCs refuse a command-shaped one](../stories/US1099-the-trd-and-the-two-stale-code-comments.md)
- [ ] [US1100: The TRD's storage sections list the committed evidence and describe the run state and lifecycle through close and sign, and the .local writer pin fails on a writer that stops writing](../stories/US1100-the-trd-s-storage-sections-list-the-committed.md)
- [ ] [US1101: The TRD's type registry, network section, ADR-003, ADR-009, ADR-012 and header match what is built on 6.2](../stories/US1101-the-trd-s-type-registry-network-section-adr.md)
- [ ] [US1102: The TSD states coverage by the CI step, describes per-unit line coverage, names both test-module conventions, maps every PRD NFR to a row and carries a 6.2 header](../stories/US1102-the-tsd-states-coverage-by-the-ci-step.md)
- [x] [US1103: The PRD's baseline reads v6.1.0 plus 6.2, no shipped feature row carries [Unreleased], and the inventory has a row for each capability shipped since July](../stories/US1103-the-prd-s-baseline-reads-v6-1-0.md)
- [x] [US1104: The PRD's business rules, NFRs and cost model match the code, its derived counts are bands, and the engagement floor reads Partial until BG0959 is Fixed](../stories/US1104-the-prd-s-business-rules-nfrs-and-cost.md)

## Acceptance Criteria (Epic Level)

- [ ] The TRD says stories and bugs execute their Verify lines and CRs and RFCs refuse a command-shaped one, naming `sdlc_md.EXECUTES_VERIFIERS` as the authority, and the two stale code comments say the same
- [ ] The TRD's storage sections list the committed evidence (actuals and forecasts shards, lessons.jsonl, the verdict logs, RPT reports, run records) and describe the live and tracked run state and the run lifecycle through close and sign
- [ ] The type registry lists charter with its vocabulary and names `META_TYPES`; the network section lists every gh caller and records the version-check GET as an ADR-004 exception
- [ ] ADR-003, ADR-009 and ADR-012 match what is built, ADR-012 carries a revision row, and the header's coverage line names v6.1.0 plus 6.2 on main
- [ ] The `.local` writer pin fails when a documented writer no longer writes the documented file

### From CR0647

- [ ] The PRD's baseline reads v6.1.0 plus 6.2 on main and no shipped feature row carries [Unreleased]
- [ ] The feature inventory carries a row for each capability shipped since July 2026 that RV0028 PRD-10 names
- [ ] The business rules, NFRs and cost model match the code: the delivery units that execute Verify lines, the groomed definition, the network paths, the read-only set and the measured tokens-per-point rate
- [ ] Derived counts are stated as bands, per prd.md:85, and per-ship history moves from feature blocks to the changelog table
- [ ] The verified detail criteria are ticked, and the engagement floor reads Partial until BG0959 is Fixed

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
