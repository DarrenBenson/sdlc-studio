# EP0318: The test suite keeps its private temp root on disk when the system temp is RAM, and clears stale roots

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0637
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0637. Delivers the work CR0637 requested.

## Story Breakdown

- [ ] [US1177: With TMPDIR unset on a tmpfs the suite's private root is made on disk and named, and an explicit TMPDIR is honoured](../stories/US1177-with-tmpdir-unset-on-a-tmpfs-the-suite.md)
- [ ] [US1178: A stale private root left by a killed run and owned by no live process is removed and named when the next run starts](../stories/US1178-a-stale-private-root-left-by-a-killed.md)

## Acceptance Criteria (Epic Level)

- [ ] Given TMPDIR unset and /tmp a tmpfs, when the suite starts, then its private root is created on a disk-backed directory (a documented default under the user's cache) and the run says where
- [ ] Given an explicit TMPDIR, when the suite starts, then it is honoured unchanged
- [ ] Given a stale private root left by a killed run, older than the newest run and owned by no live process, when the next run starts, then it is removed and named

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
