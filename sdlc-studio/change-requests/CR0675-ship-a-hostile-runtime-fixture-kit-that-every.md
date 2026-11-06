# CR-0675: Ship a hostile-runtime fixture kit that every change to the verifier core runs: a group SIGTERM and SIGINT to the caller, nested `run_verifier` callers, a consumer pytest.ini with addopts -m and filterwarnings = error beside a pytest11 plugin, a shallow clone, a non-Claude harness environment and an over-long Verify token

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_env.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** RFC0062 Phase 3, first-time-right lens: finding 3
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:15Z

## Summary

BG1190's two round-1 blockers (critic-verdicts.md:1752: a group SIGTERM no longer reaches the verifier after `start_new_session`=True, and Ctrl-C in a worker thread waits for the ceiling) and its round-2 blocker (:1760, nested callers' SIGKILL orphans grandchildren) are one class. It was carried at the review cap (BG1228), so 2.11M of agents (build 0.71M, reviews 0.46M and 0.43M, repair 0.51M) delivered none of its 2 points. Run five's US1112 (:1715, addopts -m replaced), BG1183 (:1737, filterwarnings = error with a pytest11 plugin), BG1167 (:1713, shallow clone), US0986 (:1722, the suite reads the running harness's environment) and US1113 (:1716, ENAMETOOLONG on a long token) broke on environments no fixture models, and each was found by a reviewer building that fixture by hand. Already true of the tree; BG1228 and BG1112 (Open) cover only the BG1190 instance.

## Impact

Each change to `verify_ac`, gate or `run_state` risks a round 2 or a carried unit. Consuming projects are the hostile environments, so they meet the defect whenever review misses it.

## Acceptance Criteria

- [ ] `scripts/tests/test_verifier_hostile_env.py` imports `verify_ac`, gate and `run_state`, so the existing selection runs it whenever they change, and drives each case through the shipped entry point in a scratch consumer tree.
- [ ] The kit asserts that the verifier dies with its caller's process group, SIGINT exits 130 within seconds, nested callers leave no orphan, a batch obeys the project's addopts -m, collection under filterwarnings = error with a pytest11 plugin equals a fresh pytest --collect-only, the light-tier scope check holds in a --depth 1 clone, results do not change with CLAUDECODE unset and `CURSOR_AGENT` set, and a 300-character token does not crash.
- [ ] Each case fails against a recorded mutant of the defect it models (BG1190's `start_new_session` change, US1112's addopts replacement, US1113's unbounded token).
- [ ] The kit runs in under 30 s with no network access.
- [ ] Before and after: no verifier-core unit in the next two sprints reaches round 2 on an environment the kit models.

## Recommendation

Build the kit as one test module the import-based selection already reaches, and keep the reviewer's hostile-environment probe in the brief. Saving 0.94M per run of run six's shape at the agent share (BG1190's repair 0.51M and round-2 review 0.43M; the 0.45M of orchestrator calls the lens adds lies inside the orchestrator replay), and BG1190's 2 points delivered rather than carried. Run five's shape: 3 units whose only blocker was this class, 2.25M orchestrator-inclusive. One-time build about 3 points, paid back in about two runs that touch the verifier core. It catches only the environments it models, adds coverage and removes none.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
