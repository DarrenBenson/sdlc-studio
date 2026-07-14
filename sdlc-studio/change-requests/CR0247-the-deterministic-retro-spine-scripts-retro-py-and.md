# CR-0247: The deterministic retro spine: scripts/retro.py, and ranking computed not asserted

> **Status:** Proposed
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 - operator steer
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P1
> **Type:** feature

## Summary

The learning loop as designed still leans on agent judgement at every step, and the repo's own discipline is to never hand-roll what deterministic tooling can do. There is no scripts/retro.py at all - retro is the only enforced ceremony with no script, no help file and no reference file, which is why its gate can only glob a filename (BG0123). Build the spine: retro.py new/extract/dispose/validate, and lessons.py rank. Every step that can be mechanical must be: parsing the '## Lessons' section into the store is parsing, not judgement; counting how many times a lesson's class has recurred is counting; checking each finding is filed or declined is a set difference. Judgement is reserved for what a lesson MEANS, not for whether the plumbing ran.

## Impact

Every project running a retro. Replaces judgement with mechanism wherever the step is mechanical: parsing a `## Lessons` heading is parsing, counting recurrence is counting, checking each finding is filed or declined is a set difference. Closes BG0123, whose root cause is that no tool produces or validates a retro, so the gate can only glob a filename.

**Effort:** L

## Acceptance Criteria

- [ ] scripts/retro.py exists with new / extract / dispose / validate, sharing lib/`sdlc_md.py` like every other script. Verify: test -f .claude/skills/sdlc-studio/scripts/retro.py
- [ ] retro.py extract parses the '## Lessons' section into the lessons store mechanically - 8 of 9 retros in a consuming project already carry that heading, so the input exists. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k retro
- [ ] retro.py validate checks CONTENT (required sections, at least one lesson, every finding dispositioned) and the gate leg calls it, so BG0123's 0-byte file FAILS. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k retro
- [ ] lessons.py rank computes recurrence, recency and structural-fix demotion from the artefacts - recomputed, never asserted, as reconcile does for the indexes (LL0001). Verify: python3 .claude/skills/sdlc-studio/scripts/lessons.py rank --dry-run
- [ ] The defence is validated using the bug it defends against before it is trusted (LL0010): the 0-byte retro must fail the new leg. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k retro

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
