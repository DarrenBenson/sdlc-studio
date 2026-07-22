# EP0101: A test audit lens: attack the claims tests and comments make

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0382
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0382. Delivers the work CR0382 requested.

## Story Breakdown

- [ ] [US0303: A test lens profile on the audit surface, attacking claims code and tests assert about themselves](../stories/US0303-a-test-lens-profile-on-the-audit-surface.md)
- [ ] [US0304: Lenses drawn from this project's own recorded failure modes](../stories/US0304-lenses-drawn-from-this-project-s-own-recorded.md)

## Acceptance Criteria (Epic Level)

- [ ] An audit lens profile named 'test' is selectable via --profile test alongside the existing project/skill/repo/code profiles
- [ ] The profile carries a lens asking whether a test can fail at all, by mutating the guard the test names
- [ ] The profile carries a lens asking whether a test reaches the code it claims to pin
- [ ] The profile carries a lens asking whether a test's docstring describes what it actually asserts
- [ ] The profile carries a lens asking whether a test is green for an incidental reason unrelated to the property under test
- [ ] Findings are filed or declined with a reason under the existing file-or-decline discipline; silence is not an answer
- [ ] Running the profile over this repo's own suite reproduces at least one of the three RUN-01KY1WCR prose MAJORs, proving the lens is not vacuous

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
