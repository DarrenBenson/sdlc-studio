# CR-0238: triage_noise open-codes the shared revision-row writer instead of calling it

> **Status:** Complete
> **Target:** v4.1
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson; persona; v1

## Summary

Found by the BG0109 review (2026-07-13), non-blocking. BG0109 introduced `file_finding.rev_row()` as a single choke point for the revision-history row, so the escape-and-format logic lives in one place and cannot drift by copy-paste into a fourth creator. Two of the three creators call it. `triage_noise` open-codes the identical expression instead: `sdlc_md.join_row([today`, `sdlc_md.authorship_name(raised_by)`, 'Consolidation opened']). Correct today and identical in effect, but it is precisely the drift surface `rev_row` exists to close - sitting in the very file that just demonstrated how that drift happens (`triage_noise` was the creator BG0109 missed on its first pass). The reason is presumably the `file_finding` <-> `triage_noise` load-time import cycle, which is already solved four lines below by a lazy 'import `file_finding`' inside the same function. Second, smaller gap in the same file: `triage_noise`'s index rowf carries no 'author' key, so a consolidation CR's index Author cell renders '--' while its Raised-by names the author. Unreachable on every shipped index template (the CR index has no Author column), but `row_from_header` is header-driven, so a consuming project that adds one gets the blank cell back.

## Impact

Low today (the open-coded expression is correct), but it re-opens the exact drift surface the shared writer was built to close, in the file that already proved the drift is real. Cheap to close now, invisible until it bites.

**Effort:** S

## Acceptance Criteria

- [x] `triage_noise` calls `file_finding.rev_row()` through the existing lazy import rather than open-coding its expression; the choke point is genuinely singular across all three creators
- [x] `triage_noise`'s index rowf carries the resolved author, so an Author column added by a consuming project renders the authorship of record rather than '--'

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Sam Eriksson | Raised |
| 2026-07-13 | Dani Okafor | Delivered: consolidation CR routes its revision row through `file_finding.rev_row`; index rowf carries the resolved author |
| 2026-07-14 | Dani Okafor | AC1 (singular choke point) is a structural property - the routed and open-coded forms render byte-identical output, so it is guarded by a source-scan (`_new_consolidation_cr` must call `rev_row` and must not rebuild the row inline via `join_row`), red-first against the open-coded form. AC2 (index author) is mutation-guarded. A behavioural test additionally pins the pipe-escaping property |
