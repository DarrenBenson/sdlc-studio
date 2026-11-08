# US1136: The v6.3 release notes lead with what changed for the person using it

> **Status:** Draft
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** docs/release-notes-v6.3.0.md, tools/tests/test_lean_release_notes_v63.py, changelog.d/US1136.md
> **Epic:** EP0301
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer on 6.2.0 deciding whether to take 6.3 (Maya)
**I want** release notes that open with what changed for me, name every changed default or new refusal a 6.2 habit meets beside what to do instead, and give the 6.2 upgrade path
**So that** I learn about a changed default from the notes, not from being refused by it

## Acceptance Criteria

- **AC1:** Given docs/release-notes-v6.3.0.md, then it opens with a one-sentence headline naming 6.3.0 as the current release. Its first section leads with what changed for the person using it, under four themes, each naming the units that delivered it: a run's cost is measured on whichever harness ran it (US0986, US0987, US0988, US0989, US1127); the report states the run's cost in US dollars and shows where it went (US1122, US1123, US1124, US1135); a lane runs headless in any harness's CLI, lands in one command and spawns lean agents (US1126, US1120, US1132); and the gates and commit checks are faster and truer (US1112, US1113, US1133). It links the CHANGELOG section that lists every change. Fails on: the 6.2.0 notes with the version changed, or a theme with no unit named.
  - **Verify:** tools/tests/test_lean_release_notes_v63.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you
- **AC2:** Given the notes' section on changed behaviour, then it names each change a 6.2 user meets as a new refusal or a changed default, each beside what to do instead. Among them: the shipped `release_strategy` default is now `trunk` (BG1224; `pr-required` keeps a branch and PR per change); `sprint lane land`, not the builder, now commits a lane and records its self-check (US1120); and `init` drafts the `sdlc-builder` and `sdlc-reviewer` agent definitions (US1132). It also calls out the security fix BG1213, and states that no 6.3 fragment is filed under Breaking or Removed. Fails on: a changed default named with no replacement, or a breaking change claimed that no fragment records.
  - **Verify:** tools/tests/test_lean_release_notes_v63.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do
- **AC3:** Given the notes' 'Upgrading from 6.2' section, then it says to reinstall, gives `migrate` before `migrate --apply` as commands, and states what each reports for a 6.2 project, each statement checked by running it on a 6.2-shaped fixture. Fails on: a step naming a command the shipped CLI refuses, or `--apply` given before the dry run.
  - **Verify:** tools/tests/test_lean_release_notes_v63.py::ReleaseNotesTests::test_the_62_upgrade_path_is_given
- **AC4:** Given the notes, then `tools/check_links.py` and `tools/lint-style.sh` pass and the notes carry exactly one `**v6.3.0 discloses N open defects: N Medium, N Low.**` line for `known_issues.py write --release 6.3.0` to fill. Fails on: a broken CHANGELOG anchor, an em dash, or a missing count line.
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && test "$(grep -cE '^\*\*v6\.3\.0 discloses [0-9]+ open defects: [0-9]+ Medium, [0-9]+ Low\.\*\*$' docs/release-notes-v6.3.0.md)" = 1

## Notes

- Serves: Maya Okafor, End goal 1 (she learns what changed before it refuses her).
- The content map is the document leg's: scratchpad rel63/legs/docs.json (themes, 17 changed behaviours, the repo-only units). At 8c51bd9e there were 62 fragments: 20 Added, 10 Changed, 32 Fixed, and none under Breaking, Removed or Security. Some fragments contradict each other (US0986 against US1127, US1122 against US1135): write from the final state, checked against the code.
- Model on US1110 and `tools/tests/test_lean_release_notes_v62.py`, and reuse its helpers by import. Name the mutant first: each test's docstring names the 6.2.0 notes with the version changed, or a fragment-composed draft, as the control it must refuse.
- The notes are written before the cut, so AC1's link check reads the CHANGELOG layout as it is then (`[Unreleased]` before the cut, `[6.3.0]` after), as the 6.2 test does. The cut re-points the link.
- The criteria must stay true after later releases, because `gate.py --release` executes every story's Verify at each cut.
- The gate host, the benchmark runner and this repository's own process are contributor tooling: if the notes name them, it is under a contributors heading, not among AC1's themes. BG1248, BG1249, BG1280, BG1288 and BG1289 are fixed for this release (D0427, D0428), and the fixed Codex figures belong in the cost theme.
- Figures: run seven cost 47.2M priced over 40 points (RPT0026); run eight cost 44.55M over 41 points, 1.09M per point and $118.38 (RPT0027). Read each from the signed report; an unsourced figure is refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-11-08 | Claude Opus 5.5 (grooming) | Groomed for EP0301 under D0427: user story, criteria with Verify lines and notes, modelled on EP0295 |
