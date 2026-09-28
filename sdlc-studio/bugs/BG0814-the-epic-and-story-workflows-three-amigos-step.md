# BG0814: The create path skips its two reviews: the Three Amigos step never says the seats ship with the skill, and the cohesion review is labelled Automatic though nothing runs it

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/reference-epic.md, .claude/skills/sdlc-studio/reference-story.md, .claude/skills/sdlc-studio/help/epic.md, .claude/skills/sdlc-studio/help/story.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_create_path_reviews.py, changelog.d/BG0814.md, .claude/skills/sdlc-studio/reference-workflow-personas.md
> **Evidence:** US0963 eval run v6-rc1, scenario 02-greenfield-create EB4 and EB5 (advisory) fails; transcript /tmp/evals-v6-rc1/02-greenfield-create.transcript.txt lines 1637 and 2632; operator ruling D0279 (fix before the cut)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T09:37:37Z

## Summary

Eval 02-greenfield-create on v6.0.0-rc.1 (US0963, 2026-09-28) failed advisory EB4: after epic generation the worker wrote 'The Three Amigos review was skipped because no persona files exist yet' and skipped it again for stories. The amigo seats ship with the skill (personas/seats/) and resolve in an empty project: `persona_resolve.py` resolve --seat qa --render review prints the qa charter in a fresh git init with no sdlc-studio/ tree (checked 2026-09-28). reference-epic.md step 7 and reference-story.md step 6 name the focus lists in reference-workflow-personas.md but never the command that resolves a seat, nor that project user personas are not needed, so the step reads as conditional on personas.md.

The same run failed advisory EB5: the worker generated stories and reported without the cohesion review. reference-story.md step 5 and help/story.md's heading call it '(Automatic)', yet no script performs it (`grep -il cohesion scripts/` finds none), so 'Automatic' reads as done by the tool. It also sits after step 4 'Report', so the report cannot carry its findings, and help/story.md first mentions it at line 140, past the 90 lines the worker read. The low-severity cohesion half is folded in here rather than rolled into CR0592, per D0279 (fix before the cut): same scenario, same files, same test module.

## Steps to Reproduce

Set up evals/scenarios/02-greenfield-create.json with tools/`eval_run.py` setup; run a fresh session with its prompt; the worker skips the Three Amigos step citing missing persona files.

## Proposed Fix

Each Three Amigos step (reference-epic.md, reference-story.md, and the matching help/ summaries) names `persona_resolve.py` resolve --seat <product|engineering|qa> --render review as the way to seat each amigo, and says the seats ship with the skill so the step runs whether or not the project has user personas; only --skip-personas skips it. Name the cohesion review as a step the agent performs (not 'Automatic'), move it before the Report step so the report carries its gaps, and point to it in help/story.md's opening workflow summary.

## Acceptance Criteria

- [ ] **AC1** Given the shipped epic and story workflows (reference-epic.md, reference-story.md, help/epic.md, help/story.md), then every Three Amigos step names `persona_resolve.py` resolve --seat with --render review and states the seats ship with the skill, so project personas are not a precondition. Fails on: the rc.1 wording, which names only the focus lists
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_create_path_reviews.py::CreatePathReviewTests::test_the_amigo_step_names_the_shipped_seats
  - **Verified:** yes (2026-09-28)
- [ ] **AC2** Given a fresh git repository with no sdlc-studio/ tree, when each of the three seats named by the step is resolved with the command the step shows, then each prints its charter and exits 0. Fails on: a step naming a seat or flag the resolver refuses in an empty project
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_create_path_reviews.py::CreatePathReviewTests::test_the_named_seats_resolve_in_an_empty_project
  - **Verified:** yes (2026-09-28)

- [ ] **AC3** Given reference-story.md's story workflow, then the cohesion review is a numbered step before the Report step, is not labelled Automatic, and the Report step lists its findings. Fails on: the rc.1 order (Report, then an Automatic cohesion step)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_create_path_reviews.py::CreatePathReviewTests::test_the_cohesion_review_runs_before_the_report
  - **Verified:** yes (2026-09-28)
- [ ] **AC4** Given help/story.md, then within its first 60 lines it names the cohesion review as part of /sdlc-studio story, and no heading calls it Automatic. Fails on: the rc.1 help, whose only mention is an '(Automatic)' heading at line 140
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_create_path_reviews.py::CreatePathReviewTests::test_the_story_help_names_the_cohesion_review_early
  - **Verified:** yes (2026-09-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
| 2026-09-28 | sdlc-studio v6 | Widened to eval 02's EB5 (cohesion review), AC3-AC4, 3 points; low-severity half kept out of the CR0592 roll-up per D0279 |
