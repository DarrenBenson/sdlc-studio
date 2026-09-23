# BG0744: the close refuses to file a report but a direct build --write files one anyway, skipping the token stamp and the gate verdicts the refusal protects

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Reproduced on RUN-01M33WJ3, 2026-09-23. The close refused with `terminal-gate: 4 batch unit(s) whose terminal gate is UNMET`. `sprint_report.py build --write` then filed RPT0004 with fingerprint 4e7acdbb098b6b01, Tokens 0, Per point 0, estimate accuracy NOT MEASURED, and every unit's Gate column reading `PREPARE recorded no gate verdict`. The operator asked why there were no token counts. Standing the coverage gate down through the config lane, as D0214 did for RPT0002, let the close file RPT0005 itself: 9,807,942 tokens, 272,443 per point, forecast ratio 0.49.
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint close` holds the report behind `_report_holds` - terminal-gate, unanswered-review, index-drift - on the stated ground that a run may end with work outstanding but a report may not, because it is the page a signature freezes. `sprint_report.py build --write` files a report with none of those holds applied. It is not merely a way past the refusal: `_file_the_report` also takes the run's CLOSING TOKEN STAMP and writes `report_gate_clear` before building, so a report filed the direct way reads `Tokens: 0` and `NOT MEASURED - PREPARE recorded no gate verdict` for every unit. The page looks complete and states two of its most important figures as absent.

## Steps to Reproduce

1. Open a run whose units have an unmet terminal gate.
2. `sprint.py close --retro <id>` - it refuses to file, naming the hold.
3. `sprint_report.py build --write --id <retro>` - a report is filed regardless.
4. Read its Cost section: Tokens 0, Per point 0, accuracy NOT MEASURED.

## Proposed Fix

Make `build --write` refuse when `_report_holds` is non-empty, naming the same holds and the same remedy the close names, with an explicit flag for the deliberate case. Take the closing stamp in `file_report` rather than in the close's caller, so the figure cannot depend on which route filed the page. Pin both: a held tree refuses the direct build, and a report filed either way carries a non-zero token total.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint close` holds the report behind `_report_holds` - terminal-gate, unanswered-review, index-drift - on the stated ground that a run may end with work...
- [ ] **AC2** The proposed fix lands, pinned by a test: Make `build --write` refuse when `_report_holds` is non-empty, naming the same holds and the same remedy the close names, with an explicit flag for the...

## Impact

A deliberate refusal has an unguarded route past it, and the route silently degrades the page it produces. Worse, the degradation is in the direction of looking finished: a reader sees a complete report with two figures marked absent rather than a refusal they would have had to answer. The report of record is the artefact a signature freezes, so the one command that writes it outside the lane is the one that most needs the lane's checks.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Filed |
