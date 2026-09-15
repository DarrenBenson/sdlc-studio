# CR-0576: The release cut does not list the not-stop-ship and accepted-risk rulings carried since the previous tag

> **Status:** Proposed
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
