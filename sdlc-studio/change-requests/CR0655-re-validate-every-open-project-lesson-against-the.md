# CR-0655: Re-validate every open project lesson against the current tree, closing those no longer true

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Process
> **Affects:** sdlc-studio/retros/LESSONS.md, sdlc-studio/retros/LESSONS-SUMMARY.md
> **Date:** 2026-10-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-27T23:26:09Z

## Summary

Under D0391 the 257 lessons whose horizon lapsed on 2026-10-26 were extended by one window without judgement so RUN-01M5EM9N could close. Each open lesson needs a real judgement: still true (extended with that reason) or no longer true (closed with its reason), through `lessons.py revalidate`.

## Acceptance Criteria

- [ ] Every lesson D0391 extended carries a per-lesson judgement: closed with a reason, or extended after a check against the current tree.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/lessons.py revalidate --format json
- [ ] `gate.py` reports the lessons-validity lane clean and `lessons.py summary` regenerates the digest.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/lessons.py summary --dry-run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-27 | sdlc-studio | Raised |
