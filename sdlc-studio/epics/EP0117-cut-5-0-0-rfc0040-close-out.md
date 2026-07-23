# EP0117: Cut 5.0.0 (RFC0040 close-out)

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0319
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0319. Delivers the work CR0319 requested.

## Story Breakdown

- [ ] [US0347: version bump to 5.0.0 across authoritative files, check_versions --strict green](../stories/US0347-version-bump-to-5-0-0-across-authoritative.md)
- [ ] [US0348: gate --release green on a fresh dry-run, cut the CHANGELOG 5.0.0 section, tag](../stories/US0348-gate-release-green-on-a-fresh-dry-run.md)

## Acceptance Criteria (Epic Level)

- [ ] gate.py --release passes on the release commit; `check_versions.py` --strict green at 5.0.0
- [ ] reference-upgrade.md's two-backlog migration section verified against shipped behaviour on a fresh consuming-project dry-run
- [ ] CHANGELOG 5.0.0 section cut from [Unreleased] with the Breaking block intact

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
