# US1137: The help, reference and public pages describe what 6.3 ships

> **Status:** Draft
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, README.md, llms.txt, docs/existing-users.md, docs/why-sdlc-studio.md, tools/tests/test_lean_docs_v63.py, changelog.d/US1137.md
> **Epic:** EP0301
> **Points:** 5
> **Persona:** Jonah Reyes

## User Story

**As a** team lead reading the docs before recommending 6.3 (Jonah)
**I want** the help pages, the reference and the public pages to say what 6.3 does: the meter on every harness, dollar cost, the cost anatomy, and lanes landed in one command by lean agents
**So that** a page never tells me a step 6.3 removed, or leaves out the feature that is the release

## Acceptance Criteria

- **AC1:** Given help/sprint.md's lane section, then it says the lane brief ends with the author self-check, the command that runs the unit's criteria, the line that stages exactly its Affects, and the hand-in files under `sdlc-studio/.local/lane/`. It says `sprint lane land` commits the lane and records its self-check, names the `sdlc-builder` and `sdlc-reviewer` definitions with `general-purpose` as the fallback, and no longer says the brief records the self-check or commits. Fails on: the page keeping 'record the self-check (`critic.py self-check record --unit <id>`) and commit it'.
  - **Verify:** tools/tests/test_lean_docs_v63.py::DocsV63Tests::test_the_lane_help_says_land_commits
- **AC2:** Given help/sprint.md and reference-sprint.md, then the meter paragraph says the meter reads the store of the harness running the session (claude, codex, copilot, opencode or cursor), chosen by `SDLC_STUDIO_HARNESS` or the one harness the environment signals. The `cost --anatomy` text says it reads the open run's window by default, that `--session` reads the whole session, and that a Subagent starts section flags each subagent over `cost.agent_start_budget` (30000; `off` flags none). The dollar section names `templates/model-prices.json` and its `pricing` overrides. Each statement is checked against the code it describes, and reference-sprint.md stays within the line ceiling the push gate holds it to. Fails on: a meter paragraph naming Claude transcripts as the only meter.
  - **Verify:** tools/tests/test_lean_docs_v63.py::DocsV63Tests::test_the_meter_and_cost_pages_name_every_harness_and_the_price_table
- **AC3:** Given README.md, llms.txt and docs/why-sdlc-studio.md, then README says what 6.3 adds (a run's cost, priced in US dollars per point, read from whichever of Claude Code, Codex CLI, Copilot CLI, OpenCode or Cursor ran it; a lane run headless in any of their CLIs); llms.txt names Cursor among the harnesses it installs into and names the five it meters; and the economics section of why-sdlc-studio.md states that every run's report now gives its priced cost per point. Fails on: README naming no 6.3 feature.
  - **Verify:** tools/tests/test_lean_docs_v63.py::DocsV63Tests::test_the_public_pages_name_what_63_adds
- **AC4:** Given docs/existing-users.md, then it has a 'From 6.2 to 6.3' section, first, and a 'From 6.1 to 6.2' section beneath it (the gap BG1175 records). 6.3's section says: reinstall; whether a `migrate` step is owed, checked by running `migrate` on a 6.2-shaped fixture; set `release_strategy: pr-required` to keep a branch and PR per change; and `sprint lane land` now commits a lane. Fails on: a page whose newest section is still 'From 6.0 to 6.1'.
  - **Verify:** tools/tests/test_lean_docs_v63.py::DocsV63Tests::test_existing_users_has_the_62_and_63_upgrade_paths
- **AC5:** Given the changed pages, then `tools/check_links.py`, `tools/lint-style.sh` and `python3 tools/check_budgets.py` pass. Fails on: a broken anchor, an em dash, or a page over its budget.
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && python3 tools/check_budgets.py

## Notes

- Serves: Jonah Reyes and Maya Okafor.
- The gaps are the document leg's findings 10 to 15 and 17 to 20, in scratchpad rel63/legs/docs.json, each with a location and a suggested text. Verify each suggested text against the code before using it: the leg read the code, but its wording is a draft. Finding 16 (the version pins) belongs to the cut, not here.
- reference-sprint.md is held to a line ceiling with no tolerance at push. Add a line only by cutting one, and never cut a sentence a test or a Verify line greps: run `grep -rn reference-sprint.md sdlc-studio/stories sdlc-studio/bugs | grep Verify`, then run those Verify lines.
- README's version line, install pins and current-release line are the cut's (US1111's AC3 pattern): leave them at 6.2.0.
- Each test names its mutant first: the page as it stands at 8c51bd9e must fail it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-11-08 | Claude Opus 5.5 (grooming) | Groomed for EP0301 under D0427: user story, criteria with Verify lines and notes, modelled on EP0295 |
