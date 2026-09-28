# BG0818: init guided treats a stage's own drafted scaffold, or any pre-existing file, as the stage done, so the resume point skips the stage it just drafted

> **Status:** Fixed
> **Forced-override:** 2026-09-28: --force waived 1 gate(s) on Fixed - BG0818 carries an unanswered delivery REJECT (qa-rev-a7755839's REJECT of 2026-09-28; qa-rev-a7755839's REJECT of 2026-09-28): 8 finding(s) outstanding - blocking: a non-UTF-8 AGENTS.md or prd.md now crashes init guided and status hint, because \_authored and carries\_doctrine read with strict UTF-8 inside stage\_output\_exists; non-blocking: generic template tokens such as {{version}} and {{date}} hold an authored document that quotes them, and the docstring over-claims; non-blocking: the fill-the-placeholders directive is untested; non-blocking: the AGENTS.md already present wording reads as if the user wrote a file init seeded .... A REJECT has two exits: a round-2 APPROVE from the reviewer who rejected, or carrying the unit at the review cap: that reviewer's round-2 REJECT, recorded in the open run, files the findings as a bug and drops the unit from the batch, so the run closes without it. A carried unit is still refused Done: it is delivered again in a later run and reaches Done on an APPROVE from the reviewer who rejected it (the same reviewer id). A ruling in a retro's `Known issues carried` table does not discharge it, and a `--force` waiver is recorded in the artefact's `Forced-override` field
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_stage_confirm.py, .claude/skills/sdlc-studio/help/init.md, changelog.d/BG0818.md, .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Evidence:** v6.0.0-rc.1 soak F1 and F3 (website project, WEB-init); re-run at HEAD 7e53a438 in a fresh fixture (init run, then init guided x2, then --confirm)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:23:58Z

## Summary

`init guided` reconciles the onboarding marker to the tree with `stage_output_exists`, which answers on EXISTENCE alone. The stage that was just drafted seeds its own file, so the same invocation prints `resume point: trd` with `trd <- next` while `prd` is unticked and the output says `drafted sdlc-studio/prd.md - review it, then init guided --confirm`. The next bare `init guided` then marks `prd` DONE from the unfilled template (`superseded_stages`) and drafts the TRD, so the PRD is never confirmed. The agents stage has the same shape: a brownfield repo whose AGENTS.md is framework boilerplate with no lifecycle doctrine (and a CLAUDE.md that `init run` wrote) is ticked `agents` done, so the project's agents never receive the process. Reproduced at HEAD 7e53a438 in a fresh `init run` fixture: run 1 prints resume point trd; run 2 ticks prd and drafts trd; `--confirm` then ticks trd without it being reviewed.

## Steps to Reproduce

1. `git init` an empty repo, `init.py run`. 2. `init.py guided`: prints `resume point: trd`, `[ ] prd`, `[ ] trd <- next`, `drafted sdlc-studio/prd.md`. 3. `init.py guided` again: `[x] prd` although prd.md is the unfilled template, and trd.md is drafted. 4. For the agents stage: a repo with a boilerplate AGENTS.md, `init run` then `init guided`: `[x] agents`.

## Proposed Fix

The stage just drafted stays the current stage until `--confirm` or `--skip`: compute the resume point without letting the drafted stage's own output satisfy it. A seeded singleton that still carries its template placeholders does not satisfy its stage. For `agents`, an AGENTS.md without the doctrine marker the starter carries leaves the stage open and the draft offers to append the doctrine block rather than tick the stage.

## Acceptance Criteria

- [ ] **AC1** Given a fresh project, when `init guided` drafts the PRD, then the same output names `prd` as the resume point and a second bare `init guided` still names `prd` and does not tick it. Fails on: HEAD, which prints trd and ticks prd on the second run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_stage_confirm.py::GuidedStageConfirmTests::test_the_drafted_stage_stays_current
  - **Verified:** yes (2026-09-28)
- [ ] **AC2** Given a repo whose AGENTS.md lacks the lifecycle doctrine marker, when `init guided` runs, then `agents` stays open and the output offers to append the doctrine block. Fails on: HEAD, which ticks agents because both files exist
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_stage_confirm.py::GuidedStageConfirmTests::test_boilerplate_agents_md_leaves_the_stage_open
  - **Verified:** yes (2026-09-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
| 2026-09-28 | transition set --force | forced BG0818 -> Fixed, waiving 1 gate(s): BG0818 carries an unanswered delivery REJECT (qa-rev-a7755839's REJECT of 2026-09-28; qa-rev-a7755839's REJECT of 2026-09-28): 8 finding(s) outstanding - blocking: a non-UTF-8 AGENTS.md or prd.md now crashes init guided and status hint, because \_authored and carries\_doctrine read with strict UTF-8 inside stage\_output\_exists; non-blocking: generic template tokens such as {{version}} and {{date}} hold an authored document that quotes them, and the docstring over-claims; non-blocking: the fill-the-placeholders directive is untested; non-blocking: the AGENTS.md already present wording reads as if the user wrote a file init seeded .... A REJECT has two exits: a round-2 APPROVE from the reviewer who rejected, or carrying the unit at the review cap: that reviewer's round-2 REJECT, recorded in the open run, files the findings as a bug and drops the unit from the batch, so the run closes without it. A carried unit is still refused Done: it is delivered again in a later run and reaches Done on an APPROVE from the reviewer who rejected it (the same reviewer id). A ruling in a retro's `Known issues carried` table does not discharge it, and a `--force` waiver is recorded in the artefact's `Forced-override` field |
| 2026-09-28 | sdlc-studio v6 | Forced to Fixed under operator rulings D0285 and D0286: the bounded round-3 review by qa-rev-a7755839 (brief acb059151b0a) APPROVED the unreadable-file repair with no blocking finding; critic.py refuses to record a verdict past `review.max_rounds`, so that APPROVE is recorded in D0286. BG0840 stays open for its non-blocking residuals. |
