# CR-0451: The cost of using sdlc-studio is dominated by the per-commit gate, not by the work - and that is an adoption blocker

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/reference-review.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (measured over RUN-01KYHVWK, 30 commits); agent; skill v5.0.0

## Summary

Measured over one working day on this repository: 30 commits at roughly 295 seconds of gate each, about 148 minutes. Delivering 21 units across 8 parallel agents took about 35 minutes. Productive review took about 39. The gate cost four times the delivery, and unlike a review it is paid on EVERY commit by EVERY consuming project, for ever.

The cause is that test selection is binary. `gate.is_test_relevant` answers 'should the suites run at all?', so a commit touching no script skips them entirely - but any commit touching one script runs all 4,618 tests. A three-line change to `next_id.py` re-runs the 45 sprint-rolling tests that alone take 12 seconds. The data needed to do better already ships: `repo map build` indexes symbols and imports, which is exactly the graph that maps a changed file to the tests that could possibly exercise it.

Two smaller lines sit beside it and are worth naming because together they are the whole overhead. Review currently spends most of its wall clock on mutation runs an agent drives one pytest subprocess at a time, when `mutation.py` already does that mechanically - the agent should judge survivors, not generate them. And a red-before/green-after differential harness, run by the author against the pre-fix commit, took two minutes and produced the strongest evidence of the day: it printed the live injected verifier the fix had missed. That is author work that DISPLACES review rather than adding to it.

## Impact

Who: every consuming project, and the product's core claim. sdlc-studio is adopted because it saves time and is cost-effective; a five-minute wait on every commit is the first thing a new user experiences and the thing they will measure it by. At this cost the discipline is more expensive than the vibe-coding it replaces, which is the argument against adopting it at all. What breaks in practice is worse than slowness: an un-skippable gate that costs five minutes trains people to batch commits, or to reach for --no-verify, and either defeats the gate more thoroughly than removing it would.

## Acceptance Criteria

- [ ] Test selection is by changed surface rather than binary: a commit runs the tests reachable from the files it touches, derived from the import graph the repo map already builds, not the whole suite.
- [ ] The safety net is stated and enforced: the full suite still runs somewhere it cannot be skipped - a push or release lane - so selection trades per-commit latency for a later full run, never for less coverage.
- [ ] A selected run reports what it EXCLUDED and why, so a developer can see the gate made a judgement rather than silently testing less; a file whose dependents cannot be resolved falls back to running everything, never to running nothing.
- [ ] The gate's own cost is measured and reported against a budget per commit, so a regression in gate time is visible in the same way a regression in behaviour is.
- [ ] Review drives mutation through `mutation.py` rather than an agent generating mutants one subprocess at a time, and the delivery path ships a differential harness that replays a fixed defect against the pre-fix commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (measured over RUN-01KYHVWK, 30 commits) | Raised |
