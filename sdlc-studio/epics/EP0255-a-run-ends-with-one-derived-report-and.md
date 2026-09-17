# EP0255: A run ends with one derived report, and signing it is a transaction

> **Status:** Draft
> **Derived Point Total:** 35
> **Parent:** RFC0059
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from RFC0059. Delivers the work RFC0059 requested.

## Story Breakdown

- [ ] [US0832: close splits into PREPARE, which does everything that can change facts, and SEAL, which does not](../stories/US0832-close-splits-into-prepare-which-does-everything-that.md)
- [ ] [US0833: sign writes the principal, the date and the report fingerprint against the run, and nothing else runs after it](../stories/US0833-sign-writes-the-principal-the-date-and-the.md)
- [ ] [US0834: PREPARE refuses to produce a report while any batch unit is non-terminal, any review unanswered or any index drifted](../stories/US0834-prepare-refuses-to-produce-a-report-while-any.md)
- [ ] [US0835: the report JSON of record is derived from the run's own artefacts, every figure carrying its source](../stories/US0835-the-report-json-of-record-is-derived-from.md)
- [ ] [US0836: the Markdown twin and the HTML rendering are generated from the shipped templates, and a section with no data renders NOT MEASURED by name](../stories/US0836-the-markdown-twin-and-the-html-rendering-are.md)
- [ ] [US0837: the report opens with the sprint goal verbatim and carries DORA's four keys with this project's mapping stated](../stories/US0837-the-report-opens-with-the-sprint-goal-verbatim.md)
- [ ] [US0844: the run-level token meter is stamped at run open and at report time, and the total names the sessions it covers](../stories/US0844-the-run-level-token-meter-is-stamped-at.md)
- [ ] [US0845: a report whose fingerprint no longer matches the tree renders INVALIDATED wherever it is shown](../stories/US0845-a-report-whose-fingerprint-no-longer-matches-the.md)
- [ ] [US0846: the report computes this run's change failure rate from its own push-triggered CI results, so a narrowed gate can be judged against it](../stories/US0846-the-report-computes-this-run-s-change-failure.md)

## Acceptance Criteria (Epic Level)

- [ ] **EA1** A run's close produces exactly one report, of the META type `RPT` under `sdlc-studio/reports/` (D0213), and every figure in it resolves to a source in the run's own artefacts. A figure with no source refuses the report rather than printing.
- [ ] **EA2** The operator's act is ONE command taking ONE principal, and every step that can change a fact the report states runs before it. After `sign`, a batch unit cannot be transitioned at all.
- [ ] **EA3** The report's headline cost row carries a real figure with its model and its session coverage, never `UNMEASURED` by default - the outcome RFC0059 names as worse than no report.
- [ ] **EA4** A report whose figures no longer re-derive reads INVALIDATED wherever it is shown, including in `status` for the reader who never opens it (D0213).
- [ ] **EA5** Every section with no data renders `NOT MEASURED` by name. No section is dropped, and no absent figure renders as `0`, `-` or an empty cell.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
