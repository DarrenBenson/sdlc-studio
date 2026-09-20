# CR-0590: the report absorbs the handoff, so a run ends with one page instead of two that must agree

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Date:** 2026-09-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

RFC0059 D6, ruled by the operator on 2026-09-20: the report ABSORBS the handoff. A run currently ends with two documents about itself - the report of record and a handoff guide - and the RFC names that as the drift it exists to remove.

RUN-01M2SPNS is the evidence. It reached its goal, so HO0075 read `9 delivered, 0 remaining` and carried nothing a reader needed, while still being an artefact with its own id, index row, template and link that the close had to write and keep in agreement with the report. The handoff's real value - what remains, per item, with a pointer to start from and a copilot-tail or judgement tag - is exactly what a report's remaining-work section should state, and on a run that stopped short it is the section a reader most needs.

Absorbing it also removes a defect the same run filed: BG0717, the close's handoff link leaving a trailing blank line in the retro so every close fails this project's own markdownlint. A link that is not written cannot be written badly.

## Impact

Every run, and the next agent or operator who picks one up. Today they must read two documents and know which is authoritative where; the report states what the run did and the handoff states what it did not, and nothing keeps the two consistent except care. The run that shipped the report of record demonstrated the cost: a handoff carrying nothing, a retro-link defect filed against writing it, and a close that had to sequence both.

The risk to weigh is the opposite one: the handoff is read at the START of the next run and the report at the CLOSE of the last, so folding them must not bury the remaining-work section inside a page nobody opens when planning. That is a rendering and pointer question, not a reason to keep two artefacts.

## Acceptance Criteria

- [ ] A run ends with ONE page. The report carries a remaining-work section holding what the handoff held - each remaining item, its pointer to start from, and its copilot-tail or judgement tag - and that section reads `none` by name on a run that reached its goal, rather than being absent.
- [ ] The next run's planning reads the remaining work from the report. `sprint plan --worklist` is fed from the same derivation, so the pointer the handoff used to supply still exists and still names a file the planner can open.
- [ ] No handoff artefact is created by a close. The `HO` type, its template, its index and the retro link are retired or explicitly deprecated - a type left half-alive is the drift this ruling removes, moved rather than removed.
- [ ] Existing handoffs stay readable. Runs already closed keep their HO artefacts and their index rows; nothing rewrites history, and the report's absorbed section is the shape from this change forward.
- [ ] BG0717 is closed by construction or explicitly carried: the close no longer writes a handoff link into the retro, so the trailing-blank-line defect that failed this project's markdownlint on every close cannot recur through that path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Raised |
