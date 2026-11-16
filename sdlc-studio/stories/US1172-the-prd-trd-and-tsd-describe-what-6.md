# US1172: The PRD, TRD and TSD describe what 6.4 ships

> **Status:** Done
> **Depends on:** BG1493, BG1494
> **Release:** 6.4
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_specs_v64.py, tools/tests/test_lean_trd_refresh.py, changelog.d/US1172.md
> **Epic:** EP0314
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose change board reads the specifications beside the release (Abena)
**I want** the PRD, TRD and TSD to name what 6.4 ships: the evidence annex and the release evidence pack, the escape trace, each seat's record and learnings, the second seat on a high-risk unit, the cost forecast, the records each of them commits and how the push gate holds them
**So that** the specification the board reads describes the release it approves, and every record 6.4 commits has a row naming the code that writes it

## Acceptance Criteria

- **AC1:** Given the PRD's feature inventory and feature-flags table, then the inventory has a row each, naming its units, for: the evidence annex and the report's committed run record (US0992, US0993, US0994, US0995, US0996, US0997, US0998, US1001); the release evidence pack and the evidence page (US1155, US1156, US1160, US1161); escaped-defect tracing (US1157, US1158, US1159); each seat's record (US1061, US1062, US1064); persona learnings (US1058, US1059, US1065, US1066, US1067, US1068); the risk class and the second seat (US1152, US1153, US1154); the plan's cost forecast and dispatch effort (US1150, US1151, US1165, US1166); and the resume brief and handoff (US1140, US1141, US1142). The flags table lists `risk.components`, `routing.effort`, `pricing.copilot_billing` and the `personas.memory` keys, each with the default `reference-config.md` states for it. Fails on: an inventory with no 6.4 row, or a flag default `reference-config.md` contradicts.
  - **Verify:** pytest tools/tests/test_lean_specs_v64.py::SpecsV64Tests::test_the_prd_inventory_and_flags_name_64s_features
  - **Verified:** yes (2026-11-16)
- **AC2:** Given the TRD's committed evidence and records table, then it names each record 6.4 commits with its writer, read from the code: the persona memory files `sdlc-studio/personas/memory/<persona>.md` (`persona_memory.py`), the verdict files under `sdlc-studio/reviews/verdicts/<unit>/` (issued by `critic.py brief`, bound by `critic.py record`) and a release's evidence pack `sdlc-studio/reports/evidence-pack-<version>.md` (`release_cut.py evidence-pack`). Its state section names `.local/resume-brief.md` (`sprint.py handoff`), and its data architecture names `reference-evidence-schema.md`, with the annex version it states, as the contract a consumer parses a report against. The refresh scanner checks every tracked file under `sdlc-studio/reports/`, `sdlc-studio/reviews/verdicts/` and `sdlc-studio/personas/memory/` against a row. Fails on: a tracked file in one of those trees that no row's path matches, or a row whose writer the code does not name.
  - **Verify:** pytest tools/tests/test_lean_specs_v64.py::SpecsV64Tests::test_the_trd_names_every_record_64_commits
  - **Verified:** yes (2026-11-16)
- **AC3:** Given the TSD, then it says how 6.4 tests are selected and gated: a module marked `# test-selection: sweep` joins every commit's selection (US1167); the push gate applies the green-run noise gate CI's Lint runs (BG1493); and the evidence annex's tests hold every committed report to the annex (US0992). Each statement is checked against the code or hook it describes. Fails on: a TSD that says the push gate runs the full suite and says nothing of the noise gate.
  - **Verify:** pytest tools/tests/test_lean_specs_v64.py::SpecsV64Tests::test_the_tsd_names_the_sweep_marker_and_the_push_noise_gate
  - **Verified:** yes (2026-11-16)
- **AC4:** Given the three specs after this change, then the refresh tests and the 6.3 specs test still pass. Fails on: a refresh pin broken by the edit.
  - **Verify:** shell python3 -m pytest -q tools/tests/test_lean_prd_refresh.py tools/tests/test_lean_trd_refresh.py tools/tests/test_lean_tsd_refresh.py tools/tests/test_lean_specs_v63.py
  - **Verified:** yes (2026-11-16)

## Notes

- Serves: Abena Osei, End goal 1, and Rowan Achterberg, who maintains the specs' scanners.
- Built in wave two, after BG1493: AC3 describes the push gate as BG1493 leaves it, so read the hook and gate code at that point, not the bug's proposed fix.
- `tools/tests/test_lean_trd_refresh.py` is in Affects because its committed-records scan reads only `sdlc-studio/retros/evidence/` and `sdlc-studio/reports/` today. AC2 widens it to the verdict and persona-memory trees, keeping its original mutants (US1138 amended its Affects in flight for the same scanner).
- No evidence pack is committed yet: the operator writes the 6.4.0 pack after run fifteen's sign (US1173's Notes), so prove AC2's row against a fixture pack.
- The Version and Coverage lines belong to the cut (US1173's AC5), not here.
- RFC0063's Non-Goals hold: no rewrite of the Feature Inventory, the TRD or the TSD. Add rows and amend sentences only.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-11-16 | Claude Opus 5.5 (grooming) | Groomed for EP0314 under D0474: user story, criteria with Verify lines, Release 6.4, Depends on for the wave order, and notes, modelled on EP0301 |
