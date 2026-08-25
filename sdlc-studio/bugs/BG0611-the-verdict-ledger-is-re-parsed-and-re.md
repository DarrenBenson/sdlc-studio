# BG0611: The verdict ledger is re-parsed and re-annotated on EVERY lookup, so conformance spends 122 seconds making 374 million calls to judge 23 units

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** cProfile over `gate._conformance('.', changed=False)` on 2026-08-25 at 91cd810b. Counted from the ledger: sdlc-studio/reviews/critic-verdicts.md holds 848 rows and 32 supersession records; plan-review-verdicts.md holds a further 116 rows. This is not corpus growth in artefacts - conformance judged only 23 units.
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_annotate_superseded` walks every verdict row against every supersession record, and it runs on every ledger lookup rather than once per process. Profiled over this workspace: `_matches_supersession` is called 16,837,139 times in a single whole-workspace conformance run, `sdlc_md.norm_id` 37,279,770 times, for 374 million calls and 122.7 seconds of wall clock to judge 23 units. The ledger holds 848 verdict rows and 32 supersession records - a cross-product of 27,136 - so 16.8M comparisons means the ledger is fully re-annotated about 620 times in one run. The cost is quadratic in the ledger and linear in the number of lookups, and both terms grow with every review this project records.

## Steps to Reproduce

Profile the lane directly: import gate.py and call `_conformance('.', changed=False)` under cProfile. Observed 2026-08-25 - 122.7s wall, 374,450,705 calls, with `critic.py::_matches_supersession` at 16,837,139 calls and 46.1s cumulative, and `lib/sdlc_md.py` id-normalisation at 37,279,770 calls and 40.1s. The pre-commit gate reports the same lane at 68s of a 45s budget on the scoped path, 123% over its baseline.

## Proposed Fix

Parse and annotate the ledger ONCE per process and reuse it, and index the supersession records by unit so the inner walk is a dict lookup rather than a scan. Normalising ids inside the comparison is the second multiplier: `_matches_supersession` calls `norm_id` twice per comparison, so 27,136 comparisons become 54,272 normalisations, repeated 620 times. Normalise once when the rows are read.

## Acceptance Criteria

- [ ] **AC1** Given a whole-workspace conformance run over this repository, when it completes, then `_matches_supersession` is called fewer than 100,000 times - measured in the test by counting calls, not by timing, because a wall-clock assertion is a flake on a shared machine
- [ ] **AC2** Given the same run, when its verdicts are read back, then every superseded row is annotated exactly as it is today - the paired control, so the speed-up is shown not to have changed a verdict
- [ ] **AC3** Given a ledger with a supersession record that retires a row, when the ledger is read twice in one process, then the second read does not re-walk the records - asserted by call count
- [ ] **AC4** Given a supersession record naming a unit with no matching row, when the ledger is read, then it is reported as matching nothing rather than silently ignored, exactly as today

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
