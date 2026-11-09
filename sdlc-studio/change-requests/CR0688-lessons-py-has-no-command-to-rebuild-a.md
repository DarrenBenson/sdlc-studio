# CR-0688: `lessons.py` has no command to rebuild a lost project log from the committed digest, so a project whose `.local/lessons.md` was never migrated must hand-script one `add` per lesson to close a run

> **Status:** Proposed
> **Priority:** Low
> **Type:** Enhancement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/help/lessons.md
> **Evidence:** A consuming project's close of RUN-01M6YSAV, 2026-11-09: the lessons-summary refusal, and the scripted twelve-add rebuild
> **Date:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T06:31:09Z

## Summary

6.3 commits the project lessons log at sdlc-studio/retros/LESSONS.md and moves the legacy gitignored `.local/lessons.md` there once, on the machine that holds it. A consuming project whose clone was re-made after its last close had neither file. `lessons.py summary` then correctly refused to regenerate LESSONS-SUMMARY.md from an empty log ("lists 12 lesson(s) the log ... does not hold ... Restore the log from the machine that ran the last close"). That refusal held `sprint close` at its lessons-summary step, and no machine held the log. The committed digest was the only copy. On 2026-11-09 the run's orchestrator rebuilt the log by scripting twelve `lessons.py add` calls in id order, titled from the digest, and checked in a scratch copy that the guard then passed and the digest kept all twelve lessons.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Add `lessons.py restore --from-summary`. It writes a log holding each digest item under its own id and title, with a body saying it was reconstructed and what was lost (the body, the dates and any text past the digest's cut). It refuses when a log already exists. The refusal message names it as the remedy when no log can be found.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Raised |
