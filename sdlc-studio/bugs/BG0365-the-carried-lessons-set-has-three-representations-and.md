# BG0365: The carried-lessons set has three representations and the read gate may read a different one from the one the retro writes

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; predicates mutation-killed)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0518 curates the carried set, US0520 reads it into the plan and every lane brief, and the retro's own Carried lessons section states it in prose. Those are three stores of one fact: the module constant in lessons.py, the file at retros/LESSONS-TOP.md, and the retro section. Nothing reconciles them, so a curation written to one is invisible to the reader of another and the read gate can present a stale set as current with no signal that it is stale.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review. The curated set was written by hand to retros/LESSONS-TOP.md in the previous close; the reader added in US0520 resolves its own path; the retro content check in US0518 asserts against the section. Change any one and the other two are unaffected and silent.

## Proposed Fix

Name one store authoritative - the file - and derive the other two from it: the retro section is generated from the file at validate time and the reader takes the same path from one constant. A reader that cannot find the authoritative file says so rather than presenting an empty or default set as the carried lessons.

## Acceptance Criteria

### AC1: The writer and the readers name ONE file, and it is the file the tree carries

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::CarriedSetOneTruthTests::test_the_constant_names_the_file_the_tree_actually_carries
- **Verified:** yes (2026-07-28)

### AC2: The writer and the readers read that file the same way, asserted as agreement

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::CarriedSetOneTruthTests::test_the_writer_and_the_readers_read_one_file_the_same_way
- **Verified:** yes (2026-07-28)

### AC3: The older bullet shape is still read, so the repair is a widening rather than a replacement

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::CarriedSetOneTruthTests::test_the_older_bullet_shape_is_still_read
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery. |
