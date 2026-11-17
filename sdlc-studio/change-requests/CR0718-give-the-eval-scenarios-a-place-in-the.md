# CR-0718: Give the eval scenarios a place in the release steps, or stop the TSD presenting them as a gated test level

> **Status:** In Progress
> **Decomposed-into:** EP0357
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/tsd.md, evals/README.md, tools/eval_run.py, .claude/skills/sdlc-studio/scripts/release_cut.py, .gitignore, tools/tests/test_eval_run.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, tsd lens, survived 3 of 3 refute votes; observed at sdlc-studio/tsd.md In Scope (lines 78-80), Test Strategy item 4 (lines 124-129), Coverage Targets row "Eval scenarios" (line 178), section "Eval Scenarios (flow conformance)" (lines 337-344)
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:26Z

## Summary

`sdlc-studio/tsd.md` lists the eval scenarios as a gated test level (In Scope lines 78 to 80, Test Strategy item 4, the Coverage Targets row at line 178 and the Eval Scenarios section at lines 337 to 344), with a gate failure on any blocking behaviour left ungraded. The only gate is the exit status of the `report` subcommand of `tools/eval_run.py`, and nothing invokes it: no hook lane, no npm script, no workflow, not `gate.py` and not the tag check in `release_cut.py`. `evals/README.md` says to run it by hand before tagging, yet the TSD's Before a release tag stage (line 659) does not list it. The only recorded results are two files dated 5 October, before releases 6.1 to 6.4, and the results folder is ignored by git, so a new run would leave no committed evidence. The Coverage row also names four surfaces while nine scenarios exist under `evals/scenarios/`.

## Impact

The instruction pages are most of the product and the eval scenarios are the nearest thing they have to a behaviour test. Maintainers and release readers are told that level is gated when four releases have shipped with no run on record, so a regression in routing, the independence gate or team generation would reach users unseen. The operator cutting a release has no step that tells them to run or read an eval report.

## Acceptance Criteria

- [ ] The TSD's Before a release tag stage either names the eval report step and where its result is recorded, or the TSD states that eval scenarios are run on demand and are not a gate, with the same wording in every section that mentions them.
- [ ] If the step is kept, a release check refuses or warns by name when no eval report exists for the version being cut, and a test in `tools/tests/test_eval_run.py` covers both the present and the absent case.
- [ ] A recorded eval result for a release is kept as committed evidence, or the TSD says where it is kept and why it is not committed.
- [ ] The TSD's Coverage row for eval scenarios agrees with the scenario files on disk, held by a test that fails when a scenario is added without the row changing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
