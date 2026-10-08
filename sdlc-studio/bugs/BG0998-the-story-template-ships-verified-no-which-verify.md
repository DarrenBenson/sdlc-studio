# BG0998: The story template ships Verified no, which verify_ac treats as an authored miss

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/reference-story.md, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/BG0998.md
> **Evidence:** Field report, 2026-10-07, verifying Sprint 0 on sdlc-studio-lens. Every new story was written from templates/core/story.md, so each criterion carried a bare Verified no with no reason. verify_ac.py run reported fail on every criterion, changes 0, with the selector passed but the criterion records Verified no. Deleting those lines and re-running stamped them yes.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Grok 4.7; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:15:19Z

## Summary

reference-verify.md says the Verified line is machine-maintained, and both that page and reference-story.md tell an author to mark Verified no on a new criterion until reconcile runs. The story template ships that line three times. Since BG0733, a bare Verified no with no reason is an authored disclosure: a passing selector does not stamp it and the run fails (AC7b). The unstamped state the runner already accepts is the absence of the line, which it then stamps yes. An author who follows the template cannot close the verify loop without deleting the line the template told them to write. The sticky rule for a hand-written bare no on an existing unit stays; this is the template and the two sentences that still prescribe it as the starting token.

## Steps to Reproduce

1. Copy an acceptance criterion from templates/core/story.md and replace the Verify placeholder with shell true. 2. Write it into a Draft story. 3. Run `verify_ac.py` run on that story. 4. The run reports fail=1, changes nothing, and stderr says the selector passed but the criterion records Verified no.

## Proposed Fix

Remove the three starting Verified no lines from templates/core/story.md. In reference-story.md and reference-verify.md, say the unstamped state is no Verified line, and that Verified no is a recorded miss the runner will not overwrite. Do not weaken AC7b: a hand-written bare Verified no on an existing unit remains sticky.

## Acceptance Criteria

- [ ] **AC1** A Draft story whose criterion is copied from the story template, with the Verify placeholder replaced by shell true, is stamped yes and the run reports pass=1 fail=0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_an_absent_verified_line_is_not_a_denial_when_copied_from_the_story_template

## Triage

- Reproduced at d02d28af: a Draft story whose criterion is copied from `templates/core/story.md` (lines 65, 74, 83 ship `- **Verified:** no`) with `Verify: shell true` runs as `FAIL AC1: shell true - the selector passed, but this criterion records Verified: no`. `reference-story.md:99` and `reference-verify.md:90` still prescribe the line. Pre-existing since BG0733 made a bare `Verified: no` an authored miss.
- Severity Medium stands: every story authored from the template fails its verify run until the author deletes lines the template told them to write. Changelog fragment renamed to the unit-id convention (LL0004).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Grok 4.7 | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: reproduced on current code; changelog fragment renamed to the unit id |
