# EP0255: A run ends with one derived report, and signing it is a transaction

> **Status:** Draft
> **Derived Point Total:** 30
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
