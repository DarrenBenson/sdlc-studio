# CR-0300: TSD's integration target 'every script with side effects has a write-confinement snapshot test' [HIGH] is backed by a suite that snapshots exactly one writer, with no sweep forcing new writers in

> **Status:** Proposed
> **Priority:** Medium
> **Type:** process
> **Size:** M
> **Affects:** sdlc-studio/tsd.md, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

tsd.md:170 sets the integration target - every side-effecting script fixture-tested with a before/after write-confinement snapshot - and grades it [HIGH] with no goal-not-measured caveat (unlike the unit row). `test_confinement.py` snapshot-tests five read-only scripts and exactly ONE writer (ledger.py); no other workspace writer (artifact, transition, reconcile apply, telemetry, retro, critic record, decisions, handoff, `sprint_report)` has a before/after confinement test, and nothing sweeps for a writer arriving without one (LL0013). The writer the level exists to catch - decisions.py's whole-ledger rewrite, separately filed as lockless - is one of the exempted (LL0010), and the uncommitted `sprint_report.py` writer arriving untested proves the missing-sweep mode live. CR0015 closed claiming 'TSD claim now backed' without either remedy its own text demanded. Verified 3x.

## Impact

tsd.md:170 sets the integration target - every side-effecting script fixture-tested with a before/after write-confinement snapshot - and grades it [HIGH] with no goal-not-measured caveat (unlike the unit row).

## Acceptance Criteria

- [ ] Confinement snapshots added for the major writers (artifact.py, transition.py, reconcile apply, telemetry.py, retro.py, critic record, decisions.py, handoff.py, `sprint_report.py)` in SideEffectConfinementTests
- [ ] A roster sweep fails when a side-effecting script has no confinement test (with an explicit allowlist), or tsd.md:170 is downgraded with a Known-gap caveat matching the unit row's honesty

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
