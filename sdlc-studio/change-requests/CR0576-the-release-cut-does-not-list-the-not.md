# CR-0576: The release cut does not list the not-stop-ship and accepted-risk rulings carried since the previous tag

> **Status:** Rejected
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Priority:** Medium
> **Type:** Feature
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** Stakeholder consult on CR0526's stories, RUN-01M2JA6J 2026-09-15 (sdlc-studio/reviews/consult-CR0526-stakeholders-2026-09-15.md).
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`release_cut` has no carried-table reader, so what shipped with a known issue ruled not-stop-ship or accepted-risk is not rolled up at the release.

## Impact

Release readers and the Primary persona asking 'what shipped': the rulings stay scattered across retros.

## Acceptance Criteria

- [ ] The release cut lists the not-stop-ship and accepted-risk ids carried since the previous tag in the notes it composes
- [ ] A release with none says so

## Recommendation

Roll up the carried not-stop-ship and accepted-risk ids since the previous tag, as plain text, in the release notes the cut composes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - release roll-up of not-stop-ship rulings: ruling tables are old-close ceremony; known-issues page discloses open findings |
