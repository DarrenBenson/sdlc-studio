# CR-0644: Bring the TRD's and TSD's gate architecture current: the three hooks, the boundary gates, the test stack, CI and its scheduled jobs, and the manual pre-tag steps

> **Status:** In Progress
> **Decomposed-into:** EP0290
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md
> **Evidence:** RV0028 findings TRD-2, TRD-3, TRD-4, TRD-9, TRD-21, TRD-22 and TSD-1, TSD-2, TSD-4, TSD-5, TSD-6, TSD-7, TSD-8, TSD-12, TSD-14, TSD-17, TSD-19, TSD-23 (sdlc-studio/reviews/RV0028-unified-review-before-the-second-6-2-run.md); `.githooks/pre-commit --list` (15 lanes), `.githooks/commit-msg --list` (6 lanes), `.githooks/pre-push:283-292`; trd.md:178 'The gate writes nothing'; tsd.md:535 'a hook that runs the whole gate on every commit'.
> **Date:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:48:06Z

## Summary

RV0028 found both documents describing the gate as it stood before D0180 and D0181: one pre-commit hook running the whole suite, a gate that writes nothing, a unittest-only stack and an automatic tag guard. In fact pre-commit runs cheap lanes and commit-msg runs the selected suites against an advisory 90-second budget; pre-push checks prerequisites and the red-main acknowledgement, then runs `gate.py --boundary push` (the full suite) or `--boundary release` at a tag; the runner is pytest with xdist, coverage 7.10+ measures CI, and two scheduled jobs (corpus, corpus-verify) are the only automated execution of every Verify line. `gate.py --release`, `record-green` and `tag-check` are manual pre-tag steps (D0375). Joins the second 6.2 run beside EP0288, whose remote gate changes the same sections (D0376).

## Impact

Both documents give false assurance about what a commit and a tag prove; a reader trusts a green commit as a green tree, and a rebuild from the TRD would omit the hooks entirely.

## Acceptance Criteria

- [ ] The TRD and TSD describe the commit gate (pre-commit, then commit-msg running selected suites against an advisory 90-second budget), the push gate (prerequisites, the red-main acknowledgement, `--boundary push` with the full suite) and the tag gate (`--boundary release`), each pointing at the hook's own `--list` rather than restating its lanes
- [ ] The TRD's tech stack and the TSD's framework rows name pytest with xdist, coverage 7.10 or later, PyYAML, Node 20 with markdownlint-cli and bandit, citing requirements-dev.txt as the one dependency list and the 3.10 floor job
- [ ] The TSD has a scheduled stage naming the corpus and corpus-verify jobs and their baselines, and records `gate.py --release`, `release_cut.py record-green` and `tag-check` as manual pre-tag steps (D0375)
- [ ] Neither document says the gate writes nothing: both say it writes only gitignored `.local` run state, and the gate's cost row cites its measured budget rather than 'sub-second'
- [ ] The remote gate EP0288 ships is described in the same sections in the run that ships it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Raised |
