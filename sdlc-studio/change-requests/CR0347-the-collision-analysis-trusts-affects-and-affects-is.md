# CR-0347: the collision analysis trusts Affects, and Affects is unreliable

> **Status:** Complete
> **Decomposed-into:** EP0095
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/repo_map.py
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

sprint plan derives its shared-file clusters from each unit's declared Affects. In this run four artefacts named the wrong files (US0240 named only a file it would create; US0246 named 2 of the 5 RFCs its parent required; US0252 named reconcile.py when its real surface was three other scanners; CR0295's tranche was three short), so the collision report was wrong in both directions. Correcting US0252's Affects DISSOLVED a recorded collision with US0256 while the real one - both write tests/`test_reconcile.py`, which neither declared - remained. Two agents then edited that file concurrently and the suite failed with an import error belonging to neither. Test files are almost never declared in Affects, so the cluster analysis is systematically blind to the files parallel work most often shares.

## Impact

Anyone parallelising a batch from the planner's waves is trusting a collision analysis built on data this run proved wrong four times. The failure is silent: the plan reports safe parallelism that is not safe.

## Acceptance Criteria

- [ ] the collision analysis includes the test files a unit will touch, not only its declared Affects
- [ ] a unit whose declared Affects does not resolve on disk, or omits a file its ACs name, is reported at plan time rather than at grooming

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
