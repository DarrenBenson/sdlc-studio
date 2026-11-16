# US1170: The v6.4 release notes lead with what changed for the person answering for the release

> **Status:** Done
> **Depends on:** BG1493, BG1494
> **Release:** 6.4
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** docs/release-notes-v6.4.0.md, tools/tests/test_lean_release_notes_v64.py, changelog.d/US1170.md
> **Epic:** EP0314
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering on 6.3.0 deciding whether her teams take 6.4 to the change board (Abena)
**I want** release notes that open with what changed for me, name every changed default or new refusal a 6.3 habit meets beside what to do instead, state each cost figure from the signed report it came from, and give the 6.3 upgrade path
**So that** I learn about a changed default from the notes, not from being refused by it, and every number I repeat to the board is one a report of record carries

## Acceptance Criteria

- **AC1:** Given docs/release-notes-v6.4.0.md, then it opens with a one-sentence headline naming 6.4.0 as the current release. Its first section leads with what changed for the person using it, under four themes, each naming the units that delivered it: a release carries evidence a change board accepts (US0992, US0993, US0994, US0995, US0996, US0997, US0998, US1155, US1156, US1160, US1161); a run's cost is forecast before it starts and set beside the actual, priced at each model's own rate (US0999, US1000, US1143, US1144, US1145, US1149, US1150, US1151, US1165, US1166); each review seat has a record, an escaped defect is traced to the approval that missed it, a seat learns only from a signed run, and a high-risk unit gets a second independent seat (US1011, US1012, US1013, US1015, US1058, US1059, US1061, US1062, US1064, US1065, US1066, US1067, US1068, US1152, US1153, US1154, US1157, US1158, US1159); and the front door is written for a head of engineering (US1146, US1147, US1148, US1162, US1163, US1164). It links the CHANGELOG section that lists every change. Fails on: the 6.3.0 notes with the version changed, or a theme with no unit named.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v64.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you
  - **Verified:** yes (2026-11-16)
- **AC2:** Given the notes' section on changed behaviour, then it names each change a 6.3 user meets as a new refusal or a changed default, each beside what to do instead. Among them: `critic.py record --from-verdict` refuses a verdict file whose bytes an earlier row already carries, and records a verdict written by the context that edited the unit as a self-review (US1013, US1015); the delivery verdict ledger gains a `Source` column (US1012); `pricing.copilot_billing` defaults to `tokens`, so a plan still billed per premium request sets `requests` (US1145); the report cites the committed run record `sdlc-studio/reports/runs/<RUN-ID>.json`, not `.local/run-state.json`, for each figure it reads from that record (US0997); a pytest Verify line that ran only in part fails (BG1005, BG1395); and `transition.py set <story> Ready` refuses a criterion with more than one Verify line (BG1343). It states that no 6.4 fragment is filed under Breaking, Removed or Security. Fails on: a changed default named with no replacement, or a breaking change claimed that no fragment records.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v64.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do
  - **Verified:** yes (2026-11-16)
- **AC3:** Given the notes' 'Upgrading from 6.3' section, then it says to reinstall, gives `migrate` before `migrate --apply` as commands, and states what each reports for a 6.3 project, each statement checked by running it on a 6.3-shaped fixture. It names the configuration keys 6.4 adds (`risk.components`, `routing.effort`, `pricing.copilot_billing` and the `personas.memory` keys), each with the default `reference-config.md` states for it. Fails on: a step naming a command the shipped CLI refuses, `--apply` given before the dry run, or a default `reference-config.md` contradicts.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v64.py::ReleaseNotesTests::test_the_63_upgrade_path_is_given
  - **Verified:** yes (2026-11-16)
- **AC4:** Given every cost figure the notes state (priced tokens, dollars, dollars per point or points), then each names the signed report it is read from, and the test reads that figure back from the report's committed JSON under `sdlc-studio/reports/`. Fails on: a figure with no report named, or one the named report does not carry.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v64.py::ReleaseNotesTests::test_every_cost_figure_names_its_signed_report
  - **Verified:** yes (2026-11-16)
- **AC5:** Given the notes, then `tools/check_links.py` and `tools/lint-style.sh` pass and the notes carry exactly one `**v6.4.0 discloses N open defects: N Medium, N Low.**` line for `known_issues.py write --release 6.4.0` to fill. Fails on: a broken CHANGELOG anchor, an em dash, or a missing count line.
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && test "$(grep -cE '^\*\*v6\.4\.0 discloses [0-9]+ open defects: [0-9]+ Medium, [0-9]+ Low\.\*\*$' docs/release-notes-v6.4.0.md)" = 1
  - **Verified:** yes (2026-11-16)

## Notes

- Serves: Abena Osei, End goals 1 and 3 (a release passes the change board on the run's own evidence; she knows what a point of delivery costs).
- Built in wave two, after BG1493 and BG1494 (D0474: run fifteen is the release epic). At grooming (HEAD 89539022) there were 123 fragments: 46 Added, 11 Changed, 66 Fixed, and none under Breaking, Removed or Security. Where fragments contradict each other, write from the final state, checked against the code.
- Model on US1136 and `tools/tests/test_lean_release_notes_v63.py`, and reuse its helpers by import. Name the mutant first: each test's docstring names the 6.3.0 notes with the version changed, or a fragment-composed draft, as the control it must refuse.
- The notes are written before the cut, so AC1's link check reads the CHANGELOG layout as it is then (`[Unreleased]` before the cut, `[6.4.0]` after), as the 6.3 test does. The cut (US1173) re-points the link.
- The criteria must stay true after later releases, because `gate.py --release` executes every story's Verify at each cut.
- Figures: the 6.4 runs are runs nine to fourteen, RPT0028 to RPT0033. Read each figure from the signed report's committed JSON; AC4 refuses one that names no report. Run fifteen's report is not signed when the notes are written, so they do not cite it.
- The gate host, the push gate's noise check (BG1493), the watchdog test race (BG1494), the sweep marker (US1167) and this repository's own process are contributor tooling: if the notes name them, it is under a contributors heading, not among AC1's themes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-11-16 | Claude Opus 5.5 (grooming) | Groomed for EP0314 under D0474: user story, criteria with Verify lines, Release 6.4, Depends on for the wave order, and notes, modelled on EP0301 |
