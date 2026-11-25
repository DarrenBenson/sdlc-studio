# US1329: The PRD, TRD and TSD describe what 6.5 ships

> **Status:** Done
> **Release:** 6.5
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_specs_v65.py, tools/tests/test_lean_trd_refresh.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py, changelog.d/US1329.md
> **Epic:** EP0379
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose change board reads the specifications beside the release (Abena)
**I want** the PRD, TRD and TSD to name what 6.5 ships: the persona standard and its review, the
testable persona goals, the sprint drive, the author's mutation runner, the red CI policy, delegated
and waiting signatures, the duplicate refusal and test advisories, the harness pages, the new
configuration keys and the records and state each of them writes
**So that** the specification the board reads describes the release it approves, and every record
6.5 writes has a row naming the code that writes it

## Acceptance Criteria

- **AC1:** Given the PRD's feature inventory and feature-flags table, then the inventory has a row
  each, naming its units and a location the skill or repository holds, for: the persona standard
  and persona review (US1052, US1053, US1054, US1055, US1056, US1057, US1322); testable persona
  goals and the per-seat goal review (US1036, US1039, US1040, US1046); the sprint drive and
  multi-worktree landing (US1192, US1193, US1195, US1196, US1197, US1198); the author's mutation
  runner and its replay (US1200, US1201, US1202); the red CI run policy (US1236, US1237, US1238);
  delegated and waiting signatures (US1290, US1291, US1292, US1293); the duplicate refusal and the
  plan's test advisories (US1324, US1326); and the harness and enterprise pages (US1315, US1316,
  US1317, US1318, US1319, US1320, US1321). The existing Risk class and second seat row is amended to
  name reconcile's `risk-class` drift (US1314). The flags table lists `personas.standard`,
  `ci.wait_timeout_minutes`, `ci.rerun_limit` and `review.rendered_paths`, each with the default
  `reference-config.md` states for it, and the `ci.wait_timeout_minutes` row says no script reads it
  while BG1613 is open. Fails on: the PRD at HEAD, where no row names `persona_review.py`, `sprint.py
  drive`, `gate.py --red-run`, `mutation.py run --edits` or `--distinct-from`, and the flags table
  names none of the four keys.
  - **Verify:** pytest tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_prd_inventory_and_flags_name_65s_features
  - **Verified:** yes (2026-11-25)
- **AC2:** Given the TRD's data architecture, then each record and state file 6.5 writes is named
  with its writer, read from the code: the committed records table gains the persona review ledger
  `sdlc-studio/reviews/persona-reviews.md` (`persona_review.py record`, `LEDGER_REL`), held to its
  row as pending while this repository tracks none; the JSON state files table gains
  `drive/<unit>/<step>.log` (`lib/drive.py`, through `sprint.py drive`),
  `lane/landed/<worktree>.land.json` (`lib/lanes.py`, through `sprint.py lane land`) and
  `mutation-edits-<unit>.json` (`mutation.py run --edits`); and the bug artefact's `## CI Red Runs`
  section is named with its writer, `gate.py --red-run` (`RED_RUN_SECTION`). The refresh scanner
  sweeps every tracked file under `sdlc-studio/reviews/author-mutants/` against a row, so the author
  mutant list is no longer held only as pending. Fails on: the TRD at HEAD, which names none of
  `persona-reviews.md`, `.local/drive`, `land.json`, `mutation-edits` or `CI Red Runs`; and
  `committed_trees()` at HEAD, which omits the author-mutants tree although git tracks 250 files in
  it.
  - **Verify:** pytest tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_trd_names_every_record_65_writes
  - **Verified:** yes (2026-11-25)
- **AC3:** Given the TSD, then its Mutation Testing section names the author's chosen-mutant runner,
  `mutation.py run --edits <list.json> --scope <id>`: each edit applied in a scratch copy of the
  tree and never the working tree, one verdict each of killed, survived, not-applied or error, an
  edit outside the unit's Affects reported not-applied and never counted killed; and its replay in
  `critic.py brief`, labelled the author's. Its Defect Management section names the red CI policy:
  `gate.py --red-run` answers `rerun` only while every failing test is named by an open bug whose
  title says flaky and the run's reds are fewer than `ci.rerun_limit`, `stop` past the limit or
  with a token that cannot rerun, and `regression` otherwise, filing a bug through `file_finding`;
  no answer skips or deselects a test, and it exits 0 only on `rerun`. Each statement is checked
  against the code it describes. Fails on: the TSD at HEAD, which names neither `--edits` nor
  `--red-run`.
  - **Verify:** pytest tools/tests/test_lean_specs_v65.py::SpecsV65Tests::test_the_tsd_names_the_authors_mutants_and_the_red_run_policy
  - **Verified:** yes (2026-11-25)
- **AC4:** Given the three specs after this change, then the `.local/` residue test passes, holding
  each new state row to a write in its writer's code. The refresh tests and the 6.4 specs test stay
  green; other stories' criteria (US1172, US1173 and the refresh stories) and the push's full suite
  run them, so this criterion does not run them again inside `verify_ac`'s 120-second bound. Fails
  on: a TRD with no `mutation-edits-<unit>.json` row, as at HEAD; or a state row whose writer writes
  no such path.
  - **Verify:** shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py && grep -qF 'mutation-edits-<unit>.json' sdlc-studio/trd.md
  - **Verified:** yes (2026-11-25)

## Notes

- Serves: Abena Osei, End goal 1 (quoted under US1327), and Rowan Achterberg, who maintains the
  specs' scanners.
- Built in wave one. PyYAML is already in all three specs (US1299, BG1634: PRD lines 141 to 143,
  500 and 643; TRD ADR-014 and the threat row; TSD Performance row and line 590), the TRD already
  lists the author mutant lists and verdict files (BG1621) and ADR-013 (US1293), and the TSD already
  says a commit's selection runs on the gate host (US1191): keep only the gaps above.
- `tools/tests/test_lean_trd_refresh.py` is in Affects because `committed_trees()` sweeps the
  evidence, reports, verdicts, persona memory and tranche trees but not
  `sdlc-studio/reviews/author-mutants/`, and its records test still lists `AUTHOR_MUTANTS` under
  pending though 250 files are tracked there. AC2 moves it into the sweep, keeping the original
  mutants, as US1172 widened the same scanner.
- `ci.wait_timeout_minutes` has no reader (BG1613, open, Low): the PRD row must not say it bounds
  the wait. `reference-code.md` writes the wait as `timeout 30m gh run watch <id> --exit-status`.
- The Version and Coverage lines belong to the cut (US1330's AC5), not here.
- RFC0063's Non-Goals hold: no rewrite of the Feature Inventory, the TRD or the TSD. Add rows and
  amend sentences only.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-25 | orchestrator (delegate under D0545) | Groomed for EP0379 from the product seat's draft (run twenty-seven, the v6.5.0 release epic): user story, criteria with Verify lines, Release 6.5, Depends on for the wave order, and notes, modelled on EP0314 |
| 2026-11-25 | orchestrator (delegate under D0545) | At the builder's BLOCKED: AC4's Verify names the residue test at its real path (.claude/skills/sdlc-studio/scripts/tests/, not tools/tests/), and the Affects take that test, whose path reader cannot see a state path built from parts (lib/drive.py) or returned by a same-module helper (lib/lanes.py), so AC2's two state rows can be held to their writers |
| 2026-11-25 | orchestrator (delegate under D0545) | AC4's Verify narrowed to the residue module and its grep: the five modules it named take about 212 s together, over verify_ac's 120 s bound, and the four refresh and 6.4 specs modules are already run by other stories' criteria and the full suite |
