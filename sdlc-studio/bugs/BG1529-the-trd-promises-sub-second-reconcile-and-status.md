# BG1529: The TRD promises sub-second reconcile and status, which this repository misses by more than tenfold

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md §8 Scaling Strategy (lines 735-742); §10 Performance Requirements rows 'Script run time' and 'Reconcile / status' (787-788), and the cost-model paragraph (806-807)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:57Z

## Summary

The Scaling Strategy in section 8 of `sdlc-studio/trd.md` (lines 735 to 742) says read-only scripts run in well under a second, and the Performance Requirements table in section 10 (lines 787 and 788) sets the target for reconcile and status at sub-second. On this repository's own corpus of roughly 4,200 workspace files, `reconcile.py detect` takes about 18 seconds and `status.py` about 5.5 seconds. The TRD gives no bound, growth model or mitigation for how the census cost grows with the number of artefacts, although `reconcile.py settle` runs in the pre-commit hook. No test or gate measures the target, so it is an unmeasured claim. The cost-model paragraph in the same section (lines 806 and 807) also carries a spliced sentence left by an edit and does not parse.

## Steps to Reproduce

1. In this repository, time a run of `reconcile.py detect` with the JSON format: it takes about 18 seconds of wall time.
2. Time a run of `status.py` with no arguments: it takes about 5.5 seconds, while its `--help` returns in about a tenth of a second.
3. Read `sdlc-studio/trd.md` line 738 (read-only scripts run in well under a second) and line 788 (Reconcile / status: Sub-second).
4. Read lines 806 and 807: the sentence ending 'is never a gate: a script' runs straight into 'the meter reads the store of the harness', two sentences spliced together.
5. Expected: the stated targets hold on the project's own corpus, or the document states the measured cost and how it scales. Actual: both targets are missed by more than an order of magnitude and nothing measures them.

## Proposed Fix

In `sdlc-studio/trd.md`, replace the sub-second claims in sections 8 and 10 with a statement of how the census cost scales with artefact count, the measured figures for this corpus with the date they were taken, and the command that prints the live figure. Name the pre-commit `settle` cost as part of the scaling story. Repair the spliced sentence in the cost-model paragraph so it reads as two complete sentences. Add a pin to `tools/tests/test_lean_trd_refresh.py` that the TRD no longer states a sub-second target for reconcile or status without a measuring command beside it, and that the spliced fragment is gone. If the sub-second target is to be kept as a goal instead, that is a separate performance change to file.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The Scaling Strategy in section 8 of `sdlc-studio/trd.md` (lines 735 to 742) says read-only scripts run in well under a second, and the Performance...
- [ ] **AC2** The proposed fix lands, pinned by a test: In `sdlc-studio/trd.md`, replace the sub-second claims in sections 8 and 10 with a statement of how the census cost scales with artefact count, the measured...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
