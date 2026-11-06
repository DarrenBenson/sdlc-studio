# CR-0671: Give the commit hook a sweep lane that always runs the cheap repo-wide sweep tests and refuses a staged new test module without a `test-census-subject` marker, so a sweep red is found at commit rather than at review or push

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-commit, tools/tests/test_doc_claims.py, tools/tests/test_precommit_floor_pending.py, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, tools/tests/test_skill_tests_env.py, .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py, tools/test_census.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** RFC0062 Phase 3, first-time-right lens: finding 2 (sweep lane) and its classification; ceremony lens: finding 5 (census sweeps at commit, the same BG1236 counted once)
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:22:58Z

## Summary

Three of run six's twelve round-1 blocking findings were existing sweep tests turned red that per-commit selection never ran: BG1224 (`test_doc_claims.py`, critic-verdicts.md:1758) and BG1226 (`test_precommit_floor_pending.py` and the RealRepoTests of `test_test_census.py`, :1759). The same gap created the added unit BG1236: five census tests red at the push gate (an unconfined raw git call, the root census of a new script, a test invoking the commit hook bare, an unregistered scrub site), priced at 787,928 in RPT0025. RETRO0139:18 and :25 named the fix as a Try and no CR was filed. Still true of the tree: `gate.select_tests` for scripts/sprint.py selects 135 of 494 modules and not `test_doc_claims.py`, and for .githooks/pre-commit 6 and none of the sweeps, because gate.py:2557-2620 maps only imports, loads, the test name and census-subject. Measured run times: `test_doc_claims.py` 0.24 s, `test_precommit_floor_pending.py` 10 s, `test_root_census.py` about 18 s, the `test_skill_tests_env.py` scrub sweep about 2 s; the `test_test_census.py` RealRepoTests about 250 s, too slow for every commit. BG1222 (Open) covers only the hand-copied-list census at the push gate.

## Impact

This repository pays a round 2 for each sweep red that reaches review and, in run six, a whole added unit for the ones that reached the push; each push gate costs 670 to 1,113 s on the gate host. At the agent share: BG1226's repair 0.44M and two thirds of the shared round-2 review 0.29M; BG1236's build 0.79M and reviews 0.42M and 0.25M.

## Acceptance Criteria

- [ ] A test module can declare `# test-selection: sweep`, and `gate.select_tests` adds every sweep module to each commit's selection while their recorded total run time stays within a 30 s budget; a test pins that a change to scripts/sprint.py now selects `test_doc_claims.py.`
- [ ] `test_doc_claims`, `test_precommit_floor_pending`, `test_root_census`, the `test_skill_tests_env` scrub sweep, the `test_gitutil` raw-git sweep and the commit-hook hermeticity test carry the marker, and the RealRepoTests of `test_test_census.py` stay at the push gate.
- [ ] A pre-commit lane refuses a staged new test module whose head has no `test-census-subject` marker, naming the marker to add, and passes a module that carries one.
- [ ] Replayed in a throwaway clone, the run-six commits that turned `test_doc_claims.py` and `test_precommit_floor_pending.py` red, and the landings BG1236 later repaired, are each refused at commit by the sweep lane.
- [ ] Before and after: the next sprint's report shows no round-1 blocking finding of the sweep-red class and no unit added for a push-gate sweep red.

## Recommendation

Add the sweep marker and a 30 s sweep budget to `select_tests`, mark the cheap sweeps and add the static census-marker lane; the push gate keeps the full sweep. Saving 1.95M per run at the agent share: 0.73M (the BG1224 and BG1226 round 2s) + 1.46M (BG1236 never exists) - 0.24M (12 in-place fix calls at the about 20k a call the orchestrator has left once the wave-session and sprint-drive CRs land; replay 4.85M over 243 calls). The first-time-right lens's 3.0M also counts 0.92M and 0.70M of orchestrator calls in the round-2 windows; those lie inside the orchestrator replay and are not added. The ceremony lens's census-at-commit finding (0.79M) is the same BG1236 and is counted once here. BG1236's points were not in run six's 29, so the denominator does not change. It adds checks only and about 30 s of wall clock per commit; the slow census attribution test stays at push, so the static marker check covers the one census defect run six's commit missed, not every census rule. Extends BG1222.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
