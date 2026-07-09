# EP0025: Backlog clearance and status-backlog tooling

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new

## Summary

Clear the remaining open backlog and add the tooling it exposed: a deterministic
`status.py backlog` census (CR0199), a widened provenance-tag lint guard that catches US-form
and non-leading ids (CR0201), and the residual hygiene - close the three fixed-but-unclosed
bugs, archive the over-threshold indexes, and let `validate` accept a v3 ULID id. Goal: the
open CR and bug backlog reaches 0, with the archival advisory cleared.

## Story Breakdown

- [x] [US0110: status.py backlog: non-terminal census per type and status (CR0199)](../stories/US0110-status-py-backlog-non-terminal-census-per-type.md)
- [x] [US0111: Widen the provenance-tag lint guard to US-form and non-leading ids (CR0201)](../stories/US0111-widen-the-provenance-tag-lint-guard-to-us.md)
- [ ] [US0112: Hygiene: close fixed bugs, archive over-threshold indexes, apply small deferred fixes](../stories/US0112-hygiene-close-fixed-bugs-archive-over-threshold-indexes.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
