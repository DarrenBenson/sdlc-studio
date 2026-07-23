# EP0140: A shared root resolver and rule

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0383
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0383. Delivers the work CR0383 requested.

## Story Breakdown

- [ ] [US0382: resolve_root and under_root in sdlc_md.py, documented in reference-scripts.md and best-practices/script.md, a cwd-not-root test](../stories/US0382-resolve-root-and-under-root-in-sdlc-md.md)
- [ ] [US0383: census the 62 --root scripts and fix or refile the unanchored writers, next_id first](../stories/US0383-census-the-62-root-scripts-and-fix-or.md)

## Acceptance Criteria (Epic Level)

- [ ] `resolve_root` and `under_root` (or their agreed successors) are documented in reference-scripts.md as the single sanctioned way a script resolves --root and anchors a relative output path
- [ ] A census of the 62 --root-declaring scripts is recorded, classifying each as anchored, unanchored, or a deliberate non-root surface with its reason
- [ ] Every script classified unanchored is either fixed or has a filed follow-up naming it - silence is not a classification
- [ ] best-practices/script.md states the rule for new scripts, so the next one inherits it rather than repeating the omission
- [ ] A test pins the resolver's two halves from a cwd that is NOT the root: a named root is honoured verbatim, and a default root is discovered upward rather than taken as the cwd

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
