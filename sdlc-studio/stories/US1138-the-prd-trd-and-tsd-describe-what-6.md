# US1138: The PRD, TRD and TSD describe what 6.3 ships

> **Status:** Draft
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_specs_v63.py, changelog.d/US1138.md
> **Epic:** EP0301
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As a** contributor reading the specs to change the meter or the lanes (Rowan)
**I want** the PRD, TRD and TSD to name 6.3's features, its network path and the one credential it sends
**So that** a spec never tells me the skill makes no network call or handles no secret when it does

## Acceptance Criteria

- **AC1:** Given the TRD's section 5, then its Network paths table has a row for the Cursor usage request (`lib/meter_cursor.py`, the HTTPS GET to the Cursor usage API, its override variable, its timeout and the refused redirect), and rule 6 names it. The table is derived and checked against the code: every shipped script that imports `urllib.request` appears in it. The PRD, TRD and TSD statements that the skill handles no secrets are reworded to say the skill stores none and sends one, `CURSOR_API_KEY`, only in that request's header. Fails on: a shipped script that opens a connection with no row, or 'handles no secrets' left anywhere in the three documents.
  - **Verify:** tools/tests/test_lean_specs_v63.py::SpecsV63Tests::test_every_network_path_and_the_one_credential_are_named
- **AC2:** Given the TRD's cost model and its table of JSON state files under `.local/`, then the cost model says the meter reads the store of the harness running the session and when a reading holds delegated agents' spend. The state table names each writer 6.3 added: `meter-reads.json`, `cursor-usage.jsonl`, `lane-runs/`, the `lane/` hand-in with its `landed/` copies, and `briefs/`. Fails on: the cost model keeping 'delegated and sidechain spend is supplied, not observed', or a 6.3 state file missing.
  - **Verify:** tools/tests/test_lean_specs_v63.py::SpecsV63Tests::test_the_trd_cost_model_and_state_files_match_63
- **AC3:** Given the PRD's feature inventory and feature-flags table, then the inventory has a row each for the multi-harness token meter, the price table with dollar cost, the cost anatomy, the headless lane run with `lane land`, and the lean agent definitions, each naming its units. The flags table lists `release_strategy` with its default `trunk`. Fails on: an inventory with no 6.3 row.
  - **Verify:** tools/tests/test_lean_specs_v63.py::SpecsV63Tests::test_the_prd_inventory_names_63s_features
- **AC4:** Given the three specs after this change, then the refresh tests of US1101 to US1104 still pass. Fails on: a refresh pin broken by the edit.
  - **Verify:** shell python3 -m pytest -q tools/tests/test_lean_prd_refresh.py tools/tests/test_lean_trd_refresh.py tools/tests/test_lean_tsd_refresh.py

## Notes

- Serves: Rowan Achterberg, the skill maintainer.
- The gaps are the document leg's findings 1 to 8, in scratchpad rel63/legs/docs.json. Finding 8 overlaps BG1165 (open): fix what this story's criteria name, and leave the rest of BG1165 to its own unit. Finding 9 (the Version and Coverage lines) belongs to the cut.
- AC1's table check is the regression guard: build it from the shipped scripts' imports, so a future meter that opens a connection fails it until the TRD names it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-11-08 | Claude Opus 5.5 (grooming) | Groomed for EP0301 under D0427: user story, criteria with Verify lines and notes, modelled on EP0295 |
