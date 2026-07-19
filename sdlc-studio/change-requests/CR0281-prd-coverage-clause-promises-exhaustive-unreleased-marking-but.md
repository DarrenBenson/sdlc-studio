# CR-0281: PRD coverage clause promises exhaustive [Unreleased] marking but roughly 14 committed Done epics of shipped features are absent from the feature tables

> **Status:** Complete
> **Decomposed-into:** EP0071
> **Priority:** High
> **Type:** docs
> **Size:** M
> **Affects:** sdlc-studio/prd.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

prd.md:14-18 states 'Anything not yet in a tagged release is marked [Unreleased] in the tables below', but the inventory stops at the 2026-07-14 snapshot. Absent entirely: the two-backlog request/product gates (EP0033/EP0034), the refine command family (EP0035/EP0036/EP0039), the Issue discovery type and triage ceremony (EP0038/EP0047), Three-Amigos consult in refine/triage (EP0040), command-surface audit (EP0041), the migrate orchestrator (EP0042), reconcile index creation (EP0043), audit fan-out confirm (EP0044), sprint token recording (EP0045), and close-down enforcement (EP0046) - all Done on committed main. The exhaustiveness claim is false by omission (LL0013), and the four features that ARE marked [Unreleased] carry Epic '--' against the table preamble's mapping claim. The skill's own Epic Completion Cascade requires PRD feature-table updates at epic close, so this is doctrine-violating drift, not a snapshot policy. EP0048 (in-flight) is excluded. Verified 3x by the refute panel; no CR after CR0252 tracks it.

## Impact

prd.md:14-18 states 'Anything not yet in a tagged release is marked [Unreleased] in the tables below', but the inventory stops at the 2026-07-14 snapshot.

## Acceptance Criteria

- [ ] Section 3 tables carry rows for the features shipped by EP0033-EP0047, each marked [Unreleased] with its owning epic id
- [ ] Existing [Unreleased] rows have their Epic column populated (no '--' against the preamble's mapping claim)
- [ ] The coverage note's parenthetical list of unreleased workstreams matches what the tables actually cover

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
