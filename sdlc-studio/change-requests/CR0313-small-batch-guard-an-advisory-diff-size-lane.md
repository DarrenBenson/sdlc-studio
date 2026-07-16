# CR-0313: Small-batch guard: an advisory diff-size lane flags a delivered unit whose change exceeds a batch threshold - the AI batch-size failure mode, caught deterministically

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/reference-agentic-lessons.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; agile-practice gap analysis 2026-07-16

## Summary

Gap analysis vs proven practice (research sweep 2026-07-16): DORA 2024/2025 finds AI amplifies batch size - agents produce larger changes faster, and without small-batch discipline that degrades system throughput and stability even as individual speed rises; small batches remain a core capability of elite performance (STRONG evidence). sdlc-studio enforces small batches at the planning layer (refuse >8 points, capacity budget, trunk-based doctrine) but has no check at the change layer where the AI failure mode actually appears. Add an advisory gate lane: measure the delivered unit's diff (lines changed, files touched, vs configurable thresholds seeded from this repo's measured per-point norms) and WARN - never block - when a unit's change is an outlier for its points. Advisory severity is deliberate: a legitimate mechanical sweep (a rename, a migrate) is large and fine; the lane's job is to make the outlier visible at review time, not to gate it. Pure git arithmetic, zero model tokens.

## Impact

The sizing rule bounds the ESTIMATE (points <= 8) but nothing bounds the DIFF: an agent can deliver a 3-point story as a 2,000-line change and every gate stays green - precisely the failure mode the 2024/2025 DORA data ties to AI-assisted work (throughput -1.5%, stability -7.2% where batch discipline is absent).

## Acceptance Criteria

- [ ] A gate lane computes lines-changed and files-touched for a delivered unit's commits (via the Refs/commit-id convention) and warns when either exceeds its configured threshold, defaulting off until thresholds are set
- [ ] The warning names the unit, its points, the measured size and the threshold - and states it is advisory (an expected-large change is acknowledgeable, not blocked)
- [ ] Documentation records the evidence rationale (AI batch-size amplification) and that the lane never hard-fails

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
