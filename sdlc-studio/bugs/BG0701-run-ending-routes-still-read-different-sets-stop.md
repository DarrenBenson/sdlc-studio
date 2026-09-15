# BG0701: Run-ending routes still read different sets: stop records from the parked derivation, the boundary stop ignores --retro, and stop cannot see the retro the close names

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0626-delivery-engineering.txt (engineering seat); verdicts/US0626-delivery-qa.txt (qa seat); verdicts/US0626-delivery-engineering-r2.txt (engineering seat, round two); verdicts/US0626-delivery-qa-r2.txt (qa seat, round two); verdicts/US0823-delivery-engineering.txt (engineering seat); verdicts/US0823-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`cmd_stop` reads two derivations. It refuses on `unanswered_units` but writes the record and the cost line from `blocked_by_pending`, so an unforced stop over a ruled In Progress unit or a design-rung Ready unit exits 0 and records cause pending-decision, pending 0 and `could_have_proceeded` [US0101], and prints 'being parked with it' (sprint.py:10693-10697, 10608-10611); 3f73ab64 refuses the same state with rc 1. Raised in round one and not repaired; the later relabel covered only the forced path. The boundary stop calls the predicate with no retro (sprint.py:10174) and its handoff generate passes none: with a newer RETRO0002 that rules nothing, boundary --retro RETRO0001 records US0105 as held, read from RETRO0002, while close --file-and-close --retro RETRO0001 on the same tree does not hold it. stop reads the latest retro carrying the run id (AC8), so on a state whose named retro carries no run id and rules US0101 deferred, the close checklist passes and stop refuses; that errs in the safe direction and is to spec, but the docstring at sprint.py:5813-5815 and the `cmd_stop` comment at 10664-10665 ('can never name different sets') over-claim. AC8's premise that run state records no retro id is false: a bare close records `scaffolded_retro` (sprint.py:6262), which `_apply_signoff` already reads. stop --force refuses with exit 2 when the predicate raises (sprint.py:10670), so the override cannot end a run whose set cannot be computed. help/sprint.md:93 still says an apply-signoff re-run resumes, but after a stop between sign-off and Done the re-run now refuses at the checklist (AC10's accepted consequence), so `_apply_signoff`'s signed-but-not-Done resume branch (sprint.py:6573) can no longer be reached through close.

## Steps to Reproduce

1. Open a run whose batch holds US0101 at In Progress, ruled deferred in the run's retro. python3 .claude/skills/sdlc-studio/scripts/sprint.py stop - exit 0; the archived record holds cause pending-decision, pending 0 and `could_have_proceeded` [US0101]. The same state at 3f73ab64 exits 1. 2. With RETRO0001 ruling US0105 and a newer RETRO0002 ruling nothing, sprint.py boundary --retro RETRO0001 records US0105 as held; sprint.py close --file-and-close --retro RETRO0001 on the same tree does not hold it. 3. Make the predicate raise (an unreadable carried table) and run sprint.py stop --force - exit 2.

## Proposed Fix

Write stop's record and cost line from the set it refused on, and label parked work separately. Thread --retro through `_boundary_stop` and its handoff generate. Have stop and the boundary read the named retro, else run state's `scaffolded_retro`, else the latest retro carrying the run id, and correct the docstring and AC8's premise. Let stop --force end the run with the set recorded as not computable. Correct help/sprint.md:93 and remove or re-route the unreachable resume branch.

## Acceptance Criteria

- [ ] **AC1** The proposed fix lands, pinned by a test: Write stop's record and cost line from the set it refused on, and label parked work separately.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
