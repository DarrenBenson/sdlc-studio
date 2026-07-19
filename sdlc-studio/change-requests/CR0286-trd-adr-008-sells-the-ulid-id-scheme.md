# CR-0286: TRD ADR-008 sells the ULID id scheme as absolutely collision-proof; the implementation is 2 random chars (~1/1024) in a ~17-minute timestamp bucket with the cross-machine case unguarded

> **Status:** Complete
> **Decomposed-into:** EP0071
> **Priority:** Medium
> **Type:** docs
> **Size:** S
> **Affects:** sdlc-studio/trd.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

trd.md §6 says two uncoordinated writers 'cannot mint the same id even in the same instant', ADR-008 is titled 'Collision-free ULID artefact ids' and claims 'a real entropy tail so two writers in the same instant cannot collide'. The code (lib/`sdlc_md.py`:1439-1461) is honest about the opposite: `short_ulid` keeps 6 truncated timestamp chars (~17-minute bucket) + 2 random chars, calling in-window collision 'improbable (~1/1024) rather than certain', and `mint_v3_id`'s glob-retry backstop sees only the local clone - so the exact cross-machine divergent-git-state scenario ADR-008 was written for remains 'silent until a merge'. With birthday scaling, an agent wave filing dozens of findings in one window has a material pairwise collision chance. One panel vote noted the residual is BG0086's carried caveat and `next_id.py`'s collisions detector exists as a post-hoc guard - which is exactly what the TRD should say instead of an absolute guarantee. Fix is a wording-and-residual-risk correction, not a redesign.

## Impact

trd.md §6 says two uncoordinated writers 'cannot mint the same id even in the same instant', ADR-008 is titled 'Collision-free ULID artefact ids' and claims 'a real entropy tail so two writers in the same instant cannot collide'.

## Acceptance Criteria

- [ ] §6, ADR-008 and §8 state the actual guarantee: 6+2 chars, ~1/1024 per pair inside a ~17-minute window, glob-retry as the single-writer local backstop
- [ ] ADR-008 gains a residual-risk paragraph covering the cross-machine case and naming `next_id.py`'s collisions detector as the merge-time guard
- [ ] The ADR title no longer claims 'collision-free' unconditionally

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
