# US1110: The v6.2 release notes lead with what changed for the person using it

> **Status:** Ready
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/release-notes-v6.2.0.md, tools/tests/test_lean_release_notes_v62.py, changelog.d/US1110.md
> **Epic:** EP0295
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer on 6.1.0 deciding whether to take 6.2 (Maya)
**I want** release notes that open with what changed for me, name every changed default or new refusal a 6.1 habit meets beside what to do instead, and give the 6.1 upgrade path
**So that** I learn about a changed default from the notes, not from being refused by it

## Acceptance Criteria

- **AC1:** Given docs/release-notes-v6.2.0.md, then it opens with a one-sentence headline naming 6.2.0 as the current release, and its first section leads with what changed for the person using it under four themes, each naming the units that delivered it: a reviewer judges only work its author has self-checked (US1087, US1088, US1089, US1094); one command gives a builder its whole brief (US1093); a run states what it cost, priced, over the main thread and every subagent (US1091, US1092, US1095, US1097); and the gates cost less (BG1065, BG1109). It links the CHANGELOG section that lists every change. Fails on: the 6.1.0 notes with the version changed, or a theme with no unit named.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v62.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you
- **AC2:** Given the notes' section on changed behaviour, then it names each change a 6.1 user meets as a new refusal or a changed default, each beside what to do instead, among them `review.author_self_check` (shipped as `report`; `block` refuses a brief whose unit has no matching `critic.py self-check record` row) and the single goal-review round with its `rereview: yes` answer (US1096), and it states that no 6.2 fragment is filed under Breaking or Removed. Fails on: a changed default named with no replacement, or a breaking change claimed that no fragment records.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v62.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do
- **AC3:** Given the notes' 'Upgrading from 6.1' section, then it says to reinstall, gives `migrate` before `migrate --apply` as commands, and states what each reports for a 6.1 project, each statement checked by running it on a 6.1-shaped fixture. Fails on: a step naming a command the shipped CLI refuses, or `--apply` given before the dry run.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v62.py::ReleaseNotesTests::test_the_61_upgrade_path_is_given
- **AC4:** Given the notes, then `tools/check_links.py` and `tools/lint-style.sh` pass and the notes carry exactly one `**v6.2.0 discloses N open defects: N Medium, N Low.**` line for `known_issues.py write --release 6.2.0` to fill. Fails on: a broken CHANGELOG anchor, an em dash, or a missing count line.
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && test "$(grep -cE '^\*\*v6\.2\.0 discloses [0-9]+ open defects: [0-9]+ Medium, [0-9]+ Low\.\*\*$' docs/release-notes-v6.2.0.md)" = 1

## Notes

- Serves: Maya Okafor, End goal 1 (she learns what changed before it refuses her).
- Measured 2026-11-02 at 519d125c: 71 fragments in `changelog.d/`, 11 under Added, 21 under Changed, 39 under Fixed, and none under Breaking, Removed or Security. AC2's list is wider than the fragment sections on purpose: a changed default (US1089's `review.author_self_check`, US1096's single goal-review round) surprises a 6.1 habit though it is filed under Added or Changed.
- Name the mutant first (best-practices/testing.md): each test's docstring names the 6.1.0 notes with the version changed, or a fragment-composed draft, as the control it must refuse, as `test_lean_release_notes_v61.py` does. Reuse that module's helpers by import rather than copying them.
- The notes are written before the cut, so AC1's link check reads the CHANGELOG's layout at the time (`[Unreleased]` before the cut, `[6.2.0]` after), as the 6.1 test does. US1111 re-points the link at the cut.
- The criteria must stay true after later releases, because `gate.py --release` executes every story's Verify at each cut.
- The gate host (US1075 to US1078) and the PRD, TRD and TSD refreshes are this repository's own tooling and documents. If the notes name them, it is under a heading for contributors, not among AC1's four themes.
- Figures: a run's cost comes from RPT0023 (111,425,278 priced over 69 points); the gate figures from `gate_timing.py` or the gate's own cost line. An unsourced figure is refused.
- AC3: run `migrate` and `migrate --apply` on a 6.1-shaped fixture before writing what they report; if the dry run reports nothing to change for a 6.1 project, the notes say so.
- Built before US1111, which fills the count line and links these notes from README.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Groomed for EP0295 under D0395: user story, criteria with Verify lines and notes, modelled on EP0273 |
