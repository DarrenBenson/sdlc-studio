# BG0522: BG0515's fix reproduces BG0515: a charter with an unresolved Open Question leaves the run open and the charter Queued

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Established by the engineering review seat at the RUN-01KZ79C1 boundary, driven through the shipped CLI in an isolated clone. `Spent` is declared a charter terminal at lib/sdlc_md.py:1279.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`spend_charter` routes the status write through `transition.main`, which was the right instinct - transition syncs the index and runs the status gates. But `Spent` is a charter TERMINAL in the shared registry, so transition applies its terminal Open-Questions gate to it. A charter carrying one unresolved Open Question is therefore refused.

The refusal is swallowed. `plan --write` exits 0, the run is OPEN, and the charter is still `Queued` - which is precisely BG0515's headline symptom: the queue re-offers a charter whose run is already running. The defect is reproduced through its own fix path.

Two further gaps in the same unit. `except Exception` does not catch `SystemExit`, which is what `transition.main` raises on some paths. And transition's stdout leaks unindented into `plan --write`'s output.

Separately, the AC2 verifier cannot fail on what it claims: `assertIn('"Spent"', src)` is monotone in the number of writers, so it passes harder as writers are added. A second `Spent` writer added to `cmd_next` left the full suite green (788 passed). AC2's `adding a second reddens it` is false.

## Steps to Reproduce

1. Queue a charter carrying an unresolved Open Question.
2. `sprint.py plan --worklist <file> --charter SC0001 --write` through the shipped CLI.
3. rc 0, run open, charter still Queued. Nothing in the output says the charter was refused.
4. Add a second `Spent` writer to `cmd_next` and run the suite: green.

## Proposed Fix

Decide what a refused charter means and say it. The run is already open by then, so the honest outcome is to REPORT loudly and non-zero, or to resolve the gate before opening the run - not to exit 0 with the queue silently unadvanced. Catch `SystemExit` alongside `Exception`, and capture transition's stdout rather than letting it leak. Replace the AC2 existence check with an assertion that is not monotone in writer count - count the call sites, or assert the single writer by name.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `spend_charter` routes the status write through `transition.main`, which was the right instinct - transition syncs the index and runs the status gates.
- [ ] The proposed fix lands, pinned by a test: Decide what a refused charter means and say it.

## Impact

The queue re-offers a charter whose run is already running, which is the defect BG0515 was filed to close. An operator following the shipped path gets a green plan and a queue that has not advanced, with nothing saying why.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
