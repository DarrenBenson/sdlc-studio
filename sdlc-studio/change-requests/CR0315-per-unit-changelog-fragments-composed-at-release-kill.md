# CR-0315: Per-unit CHANGELOG fragments composed at release: kill the shared-file hold-back trick that per-unit commits currently force

> **Status:** In Progress
> **Decomposed-into:** EP0058
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** CHANGELOG.md, .claude/skills/sdlc-studio/reference-outputs.md, tools/check_versions.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; sprint-run retro RUN-01KXGPBN

## Summary

The paperwork-in-the-same-commit rule collides with a single shared CHANGELOG file: unit A's bullet is written before unit B ships, so committing A cleanly means manually holding back B's text. The ecosystem's proven answer is changelog FRAGMENTS (towncrier/reno): each unit writes its own small file (e.g. changelog.d/US0180.md with section + text), trivially committed with its unit, and a deterministic compose step folds all fragments into CHANGELOG.md's [Unreleased] (or at release-tag time). `doc_coverage`'s changelog-empty check reads fragments too. No contention, no hold-back, and the release gate gains a mechanical check that no stray fragment is left behind.

## Impact

Every per-unit commit in a multi-unit sprint contends on CHANGELOG.md's [Unreleased] section: this session the agent snipped bullets to a scratch file and restored them after committing THREE times (sprint-report bullet, DORA bullet, persona bullets) so each unit's paperwork could ride its own commit - a hand-rolled, error-prone dance the same-commit paperwork rule (LL0004) forces on every disciplined sprint.

## Acceptance Criteria

- [ ] A unit's changelog entry lives in its own fragment file committed with the unit; a deterministic compose command folds fragments into CHANGELOG.md idempotently, preserving section grouping (Added/Changed/Fixed)
- [ ] The gate (or `check_versions)` fails a release tag while uncomposed fragments exist; `doc_coverage`'s changelog-empty check accepts a fragment as the entry
- [ ] reference-outputs.md documents the fragment convention; existing single-file editing keeps working for consuming projects that never adopt fragments

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
