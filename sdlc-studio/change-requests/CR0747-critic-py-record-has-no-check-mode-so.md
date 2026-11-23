# CR-0747: critic.py record has no check mode, so a reviewer cannot confirm its verdict file will record before handing back

> **Status:** Rejected
> **Priority:** Low
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/CR0747.md
> **Evidence:** run eighteen, 2026-11-19: US1198 round-two record refused on MD038; the reviewer's --dry-run refused by argparse
> **Date:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T18:24:47Z

## Summary

Reviewers write only the verdict file their brief names and must not run critic.py record. Format refusals (a code span with an edge space, MD038) then surface only when the orchestrator records, and the reviewer has to be resumed to correct its own file, since nobody else may edit a verdict. In run eighteen US1198's round-two verdict was refused this way; the reviewer tried --dry-run, which critic.py record does not have.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Add `critic.py record --check` that runs every refusal record would apply and writes nothing, and have the brief tell the reviewer to run it on its verdict file before handing back.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Raised |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Triaged by the product seat during run twenty-three planning: Rejected (D0597) |
