# EP0236: A release is published by a command, not by hand after the tag

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0545
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0545. Delivers the work CR0545 requested.

## Story Breakdown

- [ ] [US0772: A tag whose Release is missing any of its four assets is REFUSED at the release boundary](../stories/US0772-a-tag-whose-release-is-missing-any-of.md)
- [ ] [US0773: The check ships as `release_cut.py` rather than in repo-only `tools/`](../stories/US0773-the-check-ships-as-release-cut-py-rather.md)
- [ ] [US0774: A project with no release automation of its own inherits a working release step](../stories/US0774-a-project-with-no-release-automation-of-its.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a tag whose Release is missing any of its four assets, when the release boundary runs,
- [ ] Given `release_cut.py` is a SHIPPED script and `tools/` is repo-only, when the check is
- [ ] Given a project with no release automation of its own, when it runs the release step, then

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
