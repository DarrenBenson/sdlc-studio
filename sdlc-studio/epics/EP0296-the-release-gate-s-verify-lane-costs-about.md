# EP0296: The release gate's verify lane costs about one parallel suite run and can run on the gate host

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0660
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0660. Delivers the work CR0660 requested.

## Story Breakdown

- [x] [US1112: The release verify lane's pytest batch runs on every core under its own ceiling and states how many criteria it resolved](../stories/US1112-the-release-verify-lane-s-pytest-batch-runs.md)
- [ ] [US1113: The release verify lane runs the criteria its batch cannot resolve on a bounded worker pool, serial_only ones after it](../stories/US1113-the-release-verify-lane-runs-the-criteria-its.md)
- [ ] [US1114: remote-gate.sh runs one commit's release gate on the gate host and records it green only when the host passed it](../stories/US1114-remote-gate-sh-runs-one-commit-s-release.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | sdlc-studio | Created via `new` (deterministic) |
