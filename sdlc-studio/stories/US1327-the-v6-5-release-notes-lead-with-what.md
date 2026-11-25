# US1327: The v6.5 release notes lead with what changed for the person answering for the release

> **Status:** Done
> **Release:** 6.5
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/release-notes-v6.5.0.md, tools/tests/test_lean_release_notes_v65.py, changelog.d/US1327.md
> **Epic:** EP0379
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering on 6.4.0 deciding whether her teams take 6.5 to the change board (Abena)
**I want** release notes that open with what changed for me, state the defect bar this release was
held to with each figure tied to the decision of record, name every new refusal or changed default
a 6.4 habit meets beside what to do instead, state each cost figure from the signed report it came
from, and give the 6.4 upgrade path
**So that** I learn about PyYAML and the persona standard from the notes, not from being refused by
them, and every number I repeat to the board is one a record of the project carries

## Acceptance Criteria

- **AC1:** Given docs/release-notes-v6.5.0.md, then it opens with a one-sentence headline naming
  6.5.0 as the current release. Its first section leads with what changed for the person answering
  for the release, under eight themes, each naming the units or decisions that delivered it, and no
  others: 6.5 ships with fewer than 50 open defects and none at Medium or above (D0560, D0563, D0564,
  D0613); every persona and seat card is held to a written standard before it frames a brief, and
  the goal review says when nothing can check the goal (US1036, US1039, US1040, US1046, US1052,
  US1053, US1054, US1055, US1056, US1057, US1322, CR0748); a sprint walks a wave from build to
  paperwork and wakes the model only at a refusal, a warning, a REJECT, a rebase conflict or the
  wave's end, and the author's own mutants reach the reviewer replayed (US1192, US1193, US1195,
  US1196, US1197, US1198, US1200, US1201, US1202); a delegated signature names the decision that
  authorised it, and a run awaiting its signature no longer holds up the next (US1290, US1291,
  US1292, US1293); a configuration a project switched on is never read as off, because PyYAML is
  required (US1296, US1297, US1298, US1299); a red CI run on main is answered by a written policy
  (US1236, US1237, US1238); SDLC Studio is documented as a harness-agnostic Agent Skill (US1315,
  US1316, US1317, US1318, US1319, US1320, US1321); and filing and planning catch overlap before a
  run pays for it (US1314, US1324, US1326). US1190, US1191 and US1313 are named only under a
  contributors heading. It links the CHANGELOG section that lists every change. Fails on: the tree
  at HEAD, which holds no docs/release-notes-v6.5.0.md; the 6.4.0 notes with the version changed; a
  theme with no unit named.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you
  - **Verified:** yes (2026-11-25)
- **AC2:** Given the quality theme, then it states D0560's bar (fewer than 50 open defects and none
  at Medium or above), the count the drive started from (473 open, 99 of them Medium, after run
  twenty), the re-check of every open bug at HEAD by two independent seats (D0563), and the
  operator's two Won't Fix lists (139 bugs under D0564 and 128 under D0613), and it leaves the count
  at the cut to the disclosure line. Each count names the decision it is read from, and the test
  reads it back from that decision's row in `sdlc-studio/decisions.md`; each Won't Fix count is also
  read from the bug corpus as the bugs at Won't Fix whose Resolution names that decision. Fails on:
  a count with no decision named, a count the named decision does not carry, or an open-defect
  count stated anywhere but the disclosure line.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_quality_figures_name_their_decisions
  - **Verified:** yes (2026-11-25)
- **AC3:** Given the notes' section on changed behaviour, then it names each change a 6.4 user
  meets as a new refusal or a changed default, each beside what to do instead: PyYAML is required,
  the installers refuse a machine whose Python cannot import it, a command reading a present
  `.config.yaml` exits 1 naming `python3 -m pip install pyyaml`, and `gate.py` exits 2 before any
  lane (US1296, US1297, US1298, US1299); `require_ac_verification` is retired, `migrate --apply`
  removes it and `quality.done_requires_verified` is the Done gate (BG1063); a project seat card that
  breaks a blocking rule of the persona standard, or whose latest persona review failed, is refused
  at every entry point that resolves it (`persona_resolve.py resolve` exits 1, `critic.py brief` and
  the other briefs exit 2), naming the rule and the `persona_review.py brief --card <card> --seat
  <seat>` to run, unless `personas.standard: report`, which `migrate --apply` sets for a project
  holding its own cards (US1055, US1056, US1322); `sprint sign --delegated` needs `--decision`
  naming an accepted decision, and `--decision` without `--delegated` is refused (US1291);
  `file_finding.py file` refuses a duplicate of an artefact of its type with exit 1 and nothing
  written, and `--distinct-from <id>` files it anyway (US1324); `transition.py set --status Done`
  refuses a Draft or Proposed story that misses the Definition of Ready (BG0954); a run awaiting
  its signature no longer holds the run slot, so `sprint plan --write` opens the next run (US1290);
  an RFC gains a Delivered status, which `reconcile apply` and a close derive for an Accepted RFC
  whose requests are resolved (BG1569); `reconcile.py apply` raises a story's stamped `Risk-class`
  to the class the component map gives and never lowers one (US1314); and a high-class unit's
  second review seat is product on the shipped seats, never the building seat (BG1609). It names
  every fragment filed under Breaking (US1299 and BG1063 at grooming) and states that none is filed
  under Removed or Security, read from the fragments, or from the cut section once it exists, when
  the test runs. Fails on: a changed default named with no replacement; a Breaking fragment the
  section leaves out; or a refusal the code does not make, such as the US1054 fragment's claim that
  a copied 6.4 product card naming "the Primary persona, Sam" is refused (BG1655 made a lone first
  name after a comma no claim, and a fixture holding the 6.4.0 cards verbatim reports blocks=0).
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do
  - **Verified:** yes (2026-11-25)
- **AC4:** Given the notes' 'Upgrading from 6.4' section, then it says to install PyYAML
  (`python3 -m pip install pyyaml`) before reinstalling, gives `migrate` before `migrate --apply` as
  commands, and states what each does for a 6.4 project, each statement checked by running it on a
  project v6.4.0's own `init.py` made, with the 6.5.0 skill: the dry run lists `sdlc-studio/.version
  stale (skill 6.4.0 -> 6.5.0)`, and for a project holding its own persona or seat cards also `set
  personas.standard: report`, and for one carrying `require_ac_verification` that key's removal;
  `--apply` writes exactly those and nothing else. It names the configuration keys 6.5 adds,
  `personas.standard` (`block`), `ci.wait_timeout_minutes` (30), `ci.rerun_limit` (1) and
  `review.rendered_paths` (`[]`), each with the default `reference-config.md` states for it, and,
  while BG1613 is open at the commit that cut 6.5.0, says that no script in 6.5.0 reads
  `ci.wait_timeout_minutes` and names BG1613. Fails on: a step naming a command the shipped CLI
  refuses, `--apply` given before the dry run, a default `reference-config.md` contradicts,
  `review.rendered_paths` left out, or a claim that `ci.wait_timeout_minutes` bounds a wait.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_64_upgrade_path_is_given
  - **Verified:** yes (2026-11-25)
- **AC5:** Given every cost figure the notes state (priced tokens, dollars, dollars per point or
  points), then each names the signed report it is read from, one of RPT0035 to RPT0045 (runs
  sixteen to twenty-six), and the test reads that figure back from the report's committed JSON under
  `sdlc-studio/reports/`. Fails on: a figure with no report named, one the named report does not
  carry, a sum across reports no single report carries, or a report outside RPT0035 to RPT0045.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_every_cost_figure_names_its_signed_report
  - **Verified:** yes (2026-11-25)
- **AC6:** Given the notes, then `tools/check_links.py` and `tools/lint-style.sh` pass and the notes
  carry exactly one `**v6.5.0 discloses N open defects: N Medium, N Low.**` line for
  `known_issues.py write --release 6.5.0` to fill. Fails on: the tree at HEAD, which holds no notes
  file; a broken CHANGELOG anchor, an em dash, or a missing count line.
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && test "$(grep -cE '^\*\*v6\.5\.0 discloses [0-9]+ open defects: [0-9]+ Medium, [0-9]+ Low\.\*\*$' docs/release-notes-v6.5.0.md)" = 1
  - **Verified:** yes (2026-11-25)

## Notes

- Serves: Abena Osei, End goal 1 ("Every release passes the change board on the evidence the run
  produced, with no separate write-up"), End goal 2 ("Every specification and every change names an
  accountable person, not 'the agent'", through the delegated signature) and End goal 3 ("Know what
  each team's delivery costs per point and hold it to a monthly budget, whichever harness a team
  uses").
- Built in wave one. At grooming (HEAD c6e8cc7a0) `changelog.d/` held 285 fragments: 240 bugs, 44
  stories and CR0748; by section 29 Added, 17 Changed, 237 Fixed and 2 Breaking (US1299, BG1063),
  none Removed or Security. Run twenty-seven will add more before the cut: the test reads the
  fragments when it runs, never this count. Where fragments contradict each other, write from the
  final state, checked against the code: US1054's last sentence is contradicted by BG1655 (see the
  cut's Notes).
- The count line must hold digits for `known_issues.py write` to find it: its pattern is
  `\d+`, so write it as `**v6.5.0 discloses 0 open defects: 0 Medium, 0 Low.**` and let the cut
  fill it (`tools/known_issues.py` `_NOTES_COUNT`).
- Model on US1170 and `tools/tests/test_lean_release_notes_v64.py`, and reuse its helpers by import
  (`shipped`, `report_figures`, `cost_problems`'s shape with a `RUNS_65` set, `stated_defaults`).
  Name the mutant first: each test's docstring names the 6.4.0 notes with the version changed, or a
  fragment-composed draft, as the control it must refuse.
- The 6.5.0 skill is the v6.5.0 tag's tree once the tag exists, and before then this tree with its
  version read as 6.5.0, as the 6.4 test does. The AC4 run on a fixture was done that way at
  grooming (Evidence N4).
- `review.rendered_paths` (BG1606) is a fourth new key the grooming brief's list of three left
  out: `git grep rendered_paths v6.4.0` finds nothing in the scripts; HEAD's `critic.py` reads it.
  The other keys `config-defaults.yaml` gained (BG1497) were read at v6.4.0 and are not new.
- Figures: the 6.5 runs are runs sixteen to twenty-six, RPT0035 to RPT0045, all signed under
  delegation (D0528, D0535, D0539, D0545). Run twenty-seven's report is not signed when the notes
  are written, so they do not cite it. A total across reports (671 points, about $2,240) is carried
  by no single report and AC5 refuses it: cite per-report figures, such as RPT0035's $102.01 over 51
  points ($2.00 a point against $3.37 forecast) and RPT0045's $362.06 over 77 points ($4.70 a point
  against $5.46).
- The criteria must stay true after later releases, because `gate.py --release` executes every
  story's Verify at each cut. AC4's BG1613 clause is judged at the commit that cut 6.5.0 (the tag
  once it exists, else the working tree), so a later fix of BG1613 does not turn it red.
- US1190, US1191 (the gate host for a commit's suites) and US1313 (this repository's own risk map)
  are contributor tooling: name them under a contributors heading, not among AC1's themes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-25 | orchestrator (delegate under D0545) | Groomed for EP0379 from the product seat's draft (run twenty-seven, the v6.5.0 release epic): user story, criteria with Verify lines, Release 6.5, Depends on for the wave order, and notes, modelled on EP0314 |
