# CR-0709: Add lessons.py reinstate: put a retired class back in force with a recorded run and reason

> **Status:** In Progress
> **Decomposed-into:** EP0349
> **Priority:** Low
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/help/lessons.md, sdlc-studio/reviews/command-audit.md, changelog.d/CR0709.md
> **Evidence:** sdlc-studio/reviews/verdicts/BG1474/8dc244746ca5-ede8b0eb.txt, finding 3.
> **Date:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T21:31:33Z

## Summary

No shipped command puts a retired lesson class back to active without recording a hit, so BG1474 had to edit three rows of sdlc-studio/lessons.jsonl by hand (state, `retired_run` dropped, `reinstated_run` and `reinstated_reason` added). The edit was disclosed, but a step with no command is a finding (AGENTS.md). BG1474's QA review (verdict 8dc244746ca5-ede8b0eb, finding 3) noted no request was filed.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

`lessons.py reinstate --class LC-xxx --reason <why>` writes exactly the fields BG1474 wrote by hand, stamped with the open run, refusing a class that is not retired.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Raised |
