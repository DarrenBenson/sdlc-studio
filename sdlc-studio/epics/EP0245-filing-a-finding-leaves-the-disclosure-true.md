# EP0245: Filing a finding leaves the disclosure true

> **Status:** Draft
> **Derived Point Total:** 7
> **Parent:** CR0560
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0560. Delivers the work CR0560 requested.

## Story Breakdown

- [ ] [US0808: A filed Medium or Low finding is already disclosed on `docs/known-issues.md` when the filer returns](../stories/US0808-a-filed-medium-or-low-finding-is-already.md)
- [ ] [US0809: A finding filed at a BARRED severity leaves the page and the count unchanged - the paired control](../stories/US0809-a-finding-filed-at-a-barred-severity-leaves.md)
- [ ] [US0810: The release notes' disclosed count is DERIVED rather than hand-edited](../stories/US0810-the-release-notes-disclosed-count-is-derived-rather.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a Medium or Low finding is filed, when the filer returns, then `docs/known-issues.md` already discloses it - the page is derived from the corpus the filer just wrote to, so leaving it stale makes the creator the thing that breaks the guard
- [ ] Given a finding is filed at a BARRED severity, when the filer returns, then the disclosure page is unchanged and the release-notes count is unchanged - the paired control, since High and Critical are barred rather than disclosed and must not silently enter the residue
- [ ] Given the release notes state a disclosed count, when a finding is filed or closed, then that count is derived rather than hand-edited - it is the one number in the notes that tracks the corpus, and it has been corrected by hand on every filing this session

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
