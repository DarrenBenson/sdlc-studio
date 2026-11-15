# BG0998: The story template ships Verified no, which verify_ac treats as an authored miss

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/reference-story.md, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/scripts/tests/test_story_template_verified.py, changelog.d/BG0998.md
> **Evidence:** Field report, 2026-10-07, verifying Sprint 0 on a consuming project. Every new story was written from templates/core/story.md, so each criterion carried a bare Verified no with no reason. verify_ac.py run reported fail on every criterion, changes 0, with the selector passed but the criterion records Verified no. Deleting those lines and re-running stamped them yes.
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

- [ ] **AC1** Given a Draft story whose criterion is copied from templates/core/story.md with the Verify placeholder replaced by `shell true`, when `verify_ac.py run` runs on it, then it reports pass=1 fail=0 and stamps the criterion `Verified: yes`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_story_template_verified.py::StoryTemplateVerifiedTests::test_a_criterion_copied_from_the_template_is_stamped_yes
  - **Verified:** yes (2026-11-15)
- [ ] **AC2** Given reference-story.md and reference-verify.md, when their guidance on a new criterion is read, then neither tells an author to write `Verified: no` until reconcile runs, and both say a new criterion carries no Verified line and that `Verified: no` is a recorded miss the runner does not overwrite.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_story_template_verified.py::StoryTemplateVerifiedTests::test_the_references_say_a_new_criterion_carries_no_verified_line
  - **Verified:** yes (2026-11-15)
- [ ] **AC3** Given an existing criterion carrying a hand-written bare `Verified: no` and a passing selector, when `verify_ac.py run` runs, then it still reports fail=1 and leaves the line as written (BG0733's sticky rule holds).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_story_template_verified.py::StoryTemplateVerifiedTests::test_a_hand_written_bare_no_stays_sticky
  - **Verified:** yes (2026-11-15)

## Triage

- Reproduced at d02d28af: a Draft story whose criterion is copied from `templates/core/story.md` (lines 65, 74, 83 ship `- **Verified:** no`) with `Verify: shell true` runs as `FAIL AC1: shell true - the selector passed, but this criterion records Verified: no`. `reference-story.md:99` and `reference-verify.md:90` still prescribe the line. Pre-existing since BG0733 made a bare `Verified: no` an authored miss.
- Severity Medium stands: every story authored from the template fails its verify run until the author deletes lines the template told them to write. Changelog fragment renamed to the unit-id convention (LL0004).

## Notes

- AC1 must fail on: the template still shipping a bare `- **Verified:** no` under any criterion (story.md lines 67, 76 and 85 at HEAD)
- AC2 must fail on: reference-story.md:99 ('Mark `Verified: no` on every AC until reconcile runs') or reference-verify.md:90 ('ship with `Verified: no` until reconcile runs') left as they stand
- AC3 must fail on: a fix that weakens the sticky rule in verify_ac.py instead of changing the template
- Still true at HEAD 8abcfb17: templates/core/story.md:67, :76, :85; reference-story.md:99; reference-verify.md:90. `artifact.py new --template full` grafts the same core body (artifact.py:855), so template-full stories carry the line too.
- The filed AC1 named a new test inside test_verify_ac.py. Moved to a new module so BG0998 shares no file with BG1396 and BG1395, which both edit test_verify_ac.py; test_verify_ac.py is dropped from Affects because BG0998 changes no verify_ac behaviour.
- No existing test reads the template's Verified lines (checked test_lean_batch_story_fields.py, test_artifact.py, test_sdlc_md.py, test_transition.py), so no pinning test is added.
- The new module carries `# test-census-subject: .claude/skills/sdlc-studio/templates/core/story.md`.
- End goal 1 (the verify loop closes for every template-authored story) and 6.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Grok 4.7 | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: reproduced on current code; changelog fragment renamed to the unit id |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed for run fourteen: Affects, criteria with Verify lines, notes |
