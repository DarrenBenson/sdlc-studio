# CR-0664: Prevent or retire lesson LC-017 (a page-format rule mark nothing round-trips)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M6NH7W close, 2026-11-05T17:31:29Z

## Summary

The failure class LC-017 (a page-format rule mark nothing round-trips) recurred 2 time(s) after it was recorded in RUN-01M3ZAGE, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: BG0900, BG0913 and the marks BG0898, BG0901 and BG0904 added each shipped with no file-then-revalidate test, so dropping the mark invalidates signed pages while the suite stays green.

Behaviour asked of the agent: A new envelope mark ships with its round-trip pin (BG0919 holds the pattern).

Hits:

- RUN-01M5EM9N on US1091 (critic:RUN-01M5EM9N): the `PRICED_RULE` envelope mark ships without its filed-before round-trip pin. Hard-wiring `priced_rule=True` in `revalidate` (`sprint_report.py`:5342) survives `test_meter_reads_true.py` and all 61 related test modules (1,923 passed with the two BG0963 wall-clock modules left out, 1,998 with them in). Yet when executed, it turns a page built before the rule, on a run with no meter reading, from VALID into INVALIDATED (`estimates.est_actual[4]`, `est_basis[3]`, `est_basis[4]`, `est_forecast[3]` moved), because a new page carries an unmeasured `Priced cost` row there. The filed-under half is pinned: dropping the mark from `build_report` is killed by `test_lean_report_window_header` and `test_lean_reclose_keeps_window.` BG0919's RULES table in `test_lean_rule_marks_round_trip.py` holds the pattern, and `PRICED_RULE` is not in it, nor is a round trip in the unit's own test file [LC-017]
- RUN-01M6NH7W on US1117 (critic:RUN-01M6NH7W): The `priced_units` round-trip pin cannot tell whether each gated output is gated. Mutant M12 (`if head and priced_unit_rule:` -> `if head:`, `sprint_report.py`:3861) and mutant M11 (dropping `priced_unit_rule and` at `sprint_report.py`:3899) each SURVIVE `test_the_priced_unit_mark_round_trips`, each run alone in an isolated copy. Its `before` page is built by the same code with the flag off, so only the `dropped` assertion can tell, and one gated output that still differs is enough to satisfy it. The cost is real: with M12 applied, `sprint_report.py check --report RPT0024` against this tree reads INVALIDATED (`est_`*[5] "Priced per point" added, 2,540,889), and the unmutated control reads VALID (dd48acac19cd992b). No other test module names `PRICED_UNIT_RULE` or "Priced per point". [LC-017]

## Impact

Every lane and review the class reaches: each repeat of LC-017 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-017 describes cannot recur there: RUN-01M5EM9N on US1091; RUN-01M6NH7W on US1117.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-017 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | sdlc-studio | Raised |
