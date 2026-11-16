# BG1487: The README's opening says a person you can name reviews and approves each step, and it no longer points agents at llms.txt or AGENTS.md

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** README.md, tools/tests/test_readme_front_door.py, changelog.d/BG1487.md
> **Evidence:** sdlc-studio/reviews/verdicts/US1164/805ece3f9967-c7932c2e.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T23:16:04Z

## Summary

Two front-door findings from US1164's QA review (verdict 805ece3f9967-c7932c2e). (1) README.md lines 19-20 say 'a person you can name reviews and approves each step'. Each unit is reviewed by an independent seat, often an agent, and a named person signs the run once after the close; a head of engineering reading the opening is told more than the process does (pre-existing, kept through US1164's rewrite). (2) US1164 moved the agent paragraph to docs/INSTALL.md, so the README no longer points an agent at llms.txt or AGENTS.md, which a coding agent reading the front page looks for. Also pre-existing: nothing checks the anchors of README links into other pages.

## Steps to Reproduce

Read README.md lines 17-21 against reference-sprint.md's review and signing sections; grep README.md for llms.txt.

## Proposed Fix

Say each step is reviewed by a seat independent of its author and a named person signs each run; add one line pointing agents at llms.txt and AGENTS.md; pin both in tools/tests/`test_readme_front_door.py.`

## Acceptance Criteria

- [ ] **AC1** Given README.md, when its opening paragraph is read, then it claims independent review per step and a named person's signature per run, and no named person approving each step. Fails on: the old sentence.
  - **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_opening_claims_independent_review_and_one_signature_per_run
  - **Verified:** yes (2026-11-16)
- [ ] **AC2** Given README.md, when an agent reads it, then one line links llms.txt and AGENTS.md. Fails on: neither linked.
  - **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_one_line_points_agents_at_llms_txt_and_agents_md
  - **Verified:** yes (2026-11-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
| 2026-11-16 | Claude Opus 5.5 (grooming) | Groomed for EP0314: each criterion's Verify line names its own test, since the two shared one file-wide selector that passes today and could not tell them apart |
