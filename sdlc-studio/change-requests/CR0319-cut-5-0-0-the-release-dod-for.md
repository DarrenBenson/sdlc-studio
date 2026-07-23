# CR-0319: Cut 5.0.0: the release DoD for the sizing + two-backlog model (RFC0040 close-out)

> **Status:** In Progress
> **Decomposed-into:** EP0117
> **Parent:** RFC0040
> **Priority:** High
> **Type:** process
> **Size:** S
> **Affects:** CHANGELOG.md, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/reference-upgrade.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; RFC triage decisions, filed by Claude Fable 5

## Summary

RFC0040 accepted (operator): the migration machinery is largely delivered (`migrate_v3` sizing, `two_backlog.enforce` opt-in gating, reference-upgrade.md#two-backlog-migration, CHANGELOG breaking section). What remains is the release cut itself, post-freeze (~2026-07-21): final upgrade-guide read-through against shipped behaviour, version bump to 5.0.0 across authoritative files, gate.py --release green, tag. Release-gated: not before the freeze lifts.

## Impact

The breaking-but-opt-in two-backlog and sizing model sits unreleased behind the freeze; consuming projects cannot adopt it until the semver-major release is cut with its migration story attached.

## Acceptance Criteria

- [ ] gate.py --release passes on the release commit; `check_versions.py` --strict green at 5.0.0
- [ ] reference-upgrade.md's two-backlog migration section verified against shipped behaviour on a fresh consuming-project dry-run
- [ ] CHANGELOG 5.0.0 section cut from [Unreleased] with the Breaking block intact

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
