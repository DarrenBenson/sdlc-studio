# CR-0502: the mutation lane asks for evidence on a changed surface the mutation runner refuses to mutate

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Date:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (delivering US0485); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

The gate's mutation lane reports the changed surface as covered, stale or without evidence, and expects a run against it. `mutation.py run` refuses any target with uncommitted changes - correctly, and for a reason worth keeping: a mutant applied over uncommitted work cannot be told apart from that work when the file is restored, so a run that proceeded could revert it silently. The two rules meet at a contradiction: before the commit the runner will not measure the surface, and after the commit the evidence arrives too late to inform the commit the lane was gating. The lane is advisory, so nothing breaks - it just means the honest answer on every genuinely new surface is `no evidence`, and an advisory that always says the same thing gets read as scenery.

## Impact

Who: anyone delivering a new or substantially changed script through the gate. What breaks: the mutation lane cannot be satisfied for the change it is reporting on, so its verdict carries no information about whether the author actually tested their assertions. A hand-run harness (unique anchors, purged bytecode, restored bytes) is what fills the gap today, and `mutation.py register` records it as self-reported - but nothing routes the author there, so the usual outcome is an ignored warning.

## Acceptance Criteria

- [ ] An uncommitted changed surface is reported with that as the REASON, not as a bare `no evidence` - the two are different states and only one is the author's omission.
- [ ] The reason names the two ways to get measured evidence: an isolated checkout, and `register` for a hand-applied mutant with its discipline stated.

## Recommendation

Two candidates, both cheap. (1) Mutate an isolated checkout: the refusal message already names `git worktree add` as the way out, so `run --isolated` could do it rather than telling the operator to. (2) When the surface is uncommitted, say so as the reason and point at `register` plus the hand-harness discipline (unique anchor asserted, bytecode purged, patch proven to have changed the file), instead of reporting a bare `no evidence` that reads as negligence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (delivering US0485) | Raised |
