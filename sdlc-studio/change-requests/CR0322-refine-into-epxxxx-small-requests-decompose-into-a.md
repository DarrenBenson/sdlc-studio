# CR-0322: refine --into EPxxxx: small requests decompose into a shared batch epic instead of minting singletons (RFC0045 D1)

> **Status:** In Progress
> **Decomposed-into:** EP0083
> **Parent:** RFC0045
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/reference-cr.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; RFC triage decisions, filed by Claude Fable 5

## Summary

RFC0045 accepted with the batch-epic option (operator): refine apply gains --into EPxxxx to decompose a request's stories INTO an existing open epic (typically a themed session container), wiring Parent/Decomposed-into exactly as today - the request's Decomposed-into points at the shared epic, the derived point total rolls up, every existing invariant (epics the only story parents; terminal-by-derivation) untouched. A terminal or non-epic target is refused with nothing minted.

## Impact

Every S-sized CR delivered under the two-backlog discipline mints a permanent one-story epic (three in one session on 2026-07-16); at the current filing rate the epic index accretes dozens of singleton containers.

## Acceptance Criteria

- [ ] refine apply --request CRxxxx --into EPxxxx adds the minted stories to the existing epic (Parent links, derived point total, request Decomposed-into all wired); a terminal or unknown target is refused, nothing minted
- [ ] The no---into path is unchanged; the CR reference documents when to share a container epic

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
