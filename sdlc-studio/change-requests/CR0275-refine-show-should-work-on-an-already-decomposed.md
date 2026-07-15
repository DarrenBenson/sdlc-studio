# CR-0275: refine show should work on an already-decomposed request, to inform a refine add

> **Status:** Complete
> **Decomposed-into:** EP0039
> **Priority:** P3
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

refine show refuses an already-decomposed request (it shares apply's not-decomposed precondition). But now that refine add exists, an operator planning the NEXT slice of a request wants to see its content AND its existing epics - which show is the natural place for. show should accept an already-decomposed request and additionally list its current Decomposed-into epics, so it informs an add as well as a first apply.

## Impact

Minor, non-blocking (the operator can read the request file directly), but it is a real gap in the refine UX surfaced dogfooding the RFC0040 migration slice: I could not refine show RFC0040 to plan its second epic. Fits RFC0039's refine workstream. Care: show must stay read-only, and must not imply the request is un-refined when it already has epics.

## Acceptance Criteria

- [ ] refine show accepts an already-decomposed request (does not refuse it) and lists its existing Decomposed-into epics alongside the summary/impact
- [ ] show remains read-only and its refusals are limited to a non-request or an unresolvable id

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Raised |
