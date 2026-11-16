# US1171: The help, reference and public pages describe what 6.4 ships

> **Status:** Done
> **Depends on:** BG1487, BG1493, BG1494
> **Release:** 6.4
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/review.md, .claude/skills/sdlc-studio/help/retro.md, .claude/skills/sdlc-studio/help/sprint.md, README.md, llms.txt, docs/existing-users.md, docs/why-sdlc-studio.md, tools/tests/test_lean_docs_v64.py, changelog.d/US1171.md, tools/tests/test_lean_docs_v63.py
> **Epic:** EP0314
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering reading the docs before her teams adopt 6.4 (Abena)
**I want** the help pages and the public pages to say what 6.4 does: a verdict bound to the file its brief issued, each seat's record and learnings, the second seat on a high-risk unit, the escape trace, the release's evidence pack and the new configuration keys
**So that** a page never leaves out the feature my change board will ask about, or tells me a review works the way 6.3 did

## Acceptance Criteria

- **AC1:** Given help/review.md's section on the review brief, then it says: the brief names the verdict file the reviewer writes under `sdlc-studio/reviews/verdicts/<unit>/` (US1011); `critic.py record --from-verdict` binds the row to that file's bytes in the ledger's `Source` column and refuses a file an earlier row already carries (US1012, US1013); a verdict written by the context that edited the unit is recorded as a self-review (US1015); `--rejoinder` with no value quotes the seat's unanswered REJECT from the ledger (US1016); the brief carries the seat's own live learnings (US1059); and a high-class unit's brief names whether its seat is the first or the second of two independent seats (US1154). Each statement is checked against the code it describes. Fails on: help/review.md as it stands at EP0314's grooming, which names none of them.
  - **Verify:** pytest tools/tests/test_lean_docs_v64.py::DocsV64Tests::test_the_review_help_names_the_verdict_file_and_the_second_seat
  - **Verified:** yes (2026-11-16)
- **AC2:** Given help/retro.md and help/sprint.md, then help/retro.md names `retro.py seats` and the bugs it charges to the approval that missed them (US1062, US1064), the close's persona-learnings step and `sprint sign --strike` (US1067, US1068), and `escape.py trace` and `to-class` for an escaped bug (US1158, US1159), each linking the reference section that holds its detail; help/sprint.md names `routing.effort` (US1165) and `pricing.copilot_billing` (US1145), each with the default `reference-config.md` states for it. Fails on: a default `reference-config.md` contradicts, or a link to a heading that does not exist.
  - **Verify:** pytest tools/tests/test_lean_docs_v64.py::DocsV64Tests::test_the_retro_and_sprint_help_name_the_seat_record_and_the_new_keys
  - **Verified:** yes (2026-11-16)
- **AC3:** Given README.md, llms.txt and docs/why-sdlc-studio.md, then README's 'New in' line names what 6.4 adds (an evidence pack per release a change board reads, each review seat's record with escaped defects traced to the approval that missed them, and a cost forecast set beside the actual); llms.txt links docs/engineering-leaders.md and docs/evidence.md; and the evidence section of why-sdlc-studio.md names the release evidence pack and links docs/evidence.md. Fails on: README naming no 6.4 feature, or llms.txt linking neither page.
  - **Verify:** pytest tools/tests/test_lean_docs_v64.py::DocsV64Tests::test_the_public_pages_name_what_64_adds
  - **Verified:** yes (2026-11-16)
- **AC4:** Given docs/existing-users.md, then it has a 'From 6.3 to 6.4' section, first, above 'From 6.2 to 6.3'. It says: reinstall; whether a `migrate` step is owed, checked by running `migrate` on a 6.3-shaped fixture; what a 6.3 verdict ledger without the `Source` column needs, if anything; set `pricing.copilot_billing: requests` for a Copilot plan still billed per premium request; and the configuration keys 6.4 adds are optional, each with the default `reference-config.md` states for it. Fails on: a page whose newest section is still 'From 6.2 to 6.3'.
  - **Verify:** pytest tools/tests/test_lean_docs_v64.py::DocsV64Tests::test_existing_users_has_the_63_to_64_upgrade_path
  - **Verified:** yes (2026-11-16)
- **AC5:** Given the changed pages, then `tools/check_links.py`, `tools/lint-style.sh` and `python3 tools/check_budgets.py` pass. Fails on: a broken anchor, an em dash, or a page over its budget.
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && python3 tools/check_budgets.py
  - **Verified:** yes (2026-11-16)

## Notes

- Serves: Abena Osei, End goals 1 and 4, and Maya Okafor on the upgrade path.
- Built in wave two, after BG1487, which rewrites README's opening paragraph and adds a line pointing agents at llms.txt and AGENTS.md: build on its README, and leave its lines and `tools/tests/test_readme_front_door.py` as it left them.
- README's Version line, install pins and current-release line are the cut's (US1173's AC4): leave them at 6.3.0.
- reference-sprint.md is at its line ceiling (859 of 859 in `tools/check_budgets.py`) and is not in Affects: link to its sections rather than add to it. The help tree is not budgeted.
- Check each help/review.md statement against `critic.py`'s own output on a fixture unit (the brief's verdict path, the record's `Source` cell, the refusal of a reused file), not by grepping the page alone.
- docs/engineering-leaders.md and docs/evidence.md were written in run fourteen (US1161, US1162, BG1480): link them, do not restate them.
- Each test names its mutant first: the page as it stands at grooming (HEAD 89539022) must fail it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-11-16 | Claude Opus 5.5 (grooming) | Groomed for EP0314 under D0474: user story, criteria with Verify lines, Release 6.4, Depends on for the wave order, and notes, modelled on EP0301 |
