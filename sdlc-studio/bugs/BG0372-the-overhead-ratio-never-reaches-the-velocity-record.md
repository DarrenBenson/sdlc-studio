# BG0372: The overhead ratio never reaches the velocity record, so the measurement is taken and discarded

> **Status:** Fixed
> **Verification depth:** functional (the round-trip criterion failed red-first against the shipped header. Two mutants applied singly, purged, restored byte-identical - the writer's render of both columns blanked, and the reader's parse of them nulled: both KILLED. The pre-existing criteria passed against a HAND-WRITTEN header and were marked `Verified: yes` while the shipped one carried neither column; they now pin `VELOCITY_HEADER` itself)
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0523 and US0524 compute a delivery-against-overhead ratio and report it at the close. Nothing writes it to retros/VELOCITY.md, which is the only place a figure survives to be compared across sprints, so the instrument answers the question once per sprint and forgets. The measurement exists to show a trend and the trend cannot be assembled.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review by following the ratio from computation to output: it reaches the close report and stops. The velocity row written by the accuracy path carries points and tokens and no overhead term.

## Proposed Fix

Add the ratio and its unattributed remainder to the velocity row written at close, so successive sprints are comparable, and report it as unmeasured in the row when the run could not attribute it.

## Acceptance Criteria

### AC1: the velocity history carries the overhead split

- **Given** `VELOCITY_COLUMNS`, the contract between the row writer and the planner that reads back
- **When** the close records this sprint
- **Then** it declares an overhead ratio and an unattributed span, so the figure survives to be compared across sprints instead of being answered once and forgotten
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityCarriesTheOverheadSplitTests::test_a_written_overhead_term_survives_a_read_back
- **Verified:** yes (2026-08-01)
- **Note:** the previous verifier asserted only that `VELOCITY_COLUMNS` names the two keys. Those entries already existed at the commit this bug's own Revision History calls "Marked Fixed while delivering nothing", so the criterion PASSED OVER THE DEFECT and was stamped `Verified: yes` on the date of that false close. It now names the round trip, which is the actual claim.

### AC2: the reader matches the header it writes

- **Given** a header row carrying the new columns
- **When** the close records this sprint
- **Then** the reader resolves both, so a written column that no reader parses cannot land silently on disk
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityCarriesTheOverheadSplitTests::test_the_column_header_is_matched_by_the_reader
- **Verified:** yes (2026-07-29)

### AC3: an unattributable run records absence, never zero

- **Given** a run whose overhead cannot be attributed
- **When** the close records this sprint
- **Then** no overhead term is written at all - a 0 in this file reads as a sprint with no overhead, and the next plan reads this file as evidence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityCarriesTheOverheadSplitTests::test_an_unattributable_run_records_absence_not_zero
- **Verified:** yes (2026-07-29)

### AC4: a broken report never fails the close

- **Given** an unreadable root
- **When** the close records this sprint
- **Then** the terms are absent and the close proceeds, because a reporting figure is not worth a refused ceremony
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityCarriesTheOverheadSplitTests::test_a_broken_report_never_fails_the_close
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
| 2026-07-29 | Claude Opus 5 | REOPENED at the closing review. The fix added `overhead_ratio` and `unattributed_s` to `VELOCITY_COLUMNS` and to the row dict, and touched neither `VELOCITY_HEADER` nor the row emitter - so nothing reaches the file the measurement exists to survive in. `unattributed_s` is also 0.0 by construction (`delivery` is defined as `total - overhead`, so the residue is identically zero) and `_overhead_terms` blanks two of three components, computing a different number from the close report. The two tests asserted a constant and a hand-written header the writer never emits. Marked Fixed while delivering nothing; the residue is BG0406. |
