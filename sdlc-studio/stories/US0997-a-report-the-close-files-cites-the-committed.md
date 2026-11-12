# US0997: A report the close files cites the committed run record, never .local/run-state.json

> **Status:** Done
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/US0997.md, .claude/skills/sdlc-studio/scripts/tests/test_report_build_named_run.py
> **Epic:** EP0276
> **Points:** 3
> **Persona:** Graham Doyle

## User Story

**As** a team lead reviewing a teammate's sprint report from my own clone
**I want** every figure the close files from the run record, the frozen CI runs included, to cite the run record committed beside the report
**So that** each provenance link on the page opens in my clone, which never holds the closer's .local/ directory

## Acceptance Criteria

- **AC1:** Given a run closed through `sprint close`, when the filed RPT JSON is read, then every figure derived from the run record cites `sdlc-studio/reports/runs/<RUN-ID>.json`, and none cites `sdlc-studio/.local/run-state.json`, including the not-measured reasons the Markdown twin prints as the source it consulted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_close_cites_the_tracked_run_record
  - **Verified:** yes (2026-11-12)
- **AC2:** Given a run whose CI runs the close froze on its record, when the filed page is read, then each DORA figure derived from those runs cites the tracked run record first, followed by the forge reading that filled it (`gh run list`, or its failure reason), while the figures counted from git history keep citing it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_frozen_ci_figures_cite_the_tracked_record
  - **Verified:** yes (2026-11-12)
- **AC3:** Given that run signed with `sprint sign` and committed, when a fresh clone holding no `.local/` reads the page, then the run-record path its figures cite exists in that clone and carries the signature the page carries, and `sprint_report check` there reads VALID.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_the_cited_record_opens_in_a_fresh_clone
  - **Verified:** yes (2026-11-12)
- **AC4:** Given a signed page whose figures cite `sdlc-studio/.local/run-state.json`, as every page filed before this change does, and a page filed after the change, when `sprint_report check` runs on each in a fresh clone, then both read VALID and only the later page cites the tracked record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_a_page_citing_local_still_checks_valid
  - **Verified:** yes (2026-11-12)

## Notes

- Release: 6.4, run ten (D0461); was 6.3 (D0388) (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: build_report keeps citing state_rel, the path `_run_state_for` happened to read the record from, which at a close is the live .local file
- AC2 must fail on: `_ci_runs` returning the frozen reading's own source alone (sprint_report.py:3039-3041), so ten to fifteen DORA figures per page cite a command and no committed file
- AC3 must fail on: citing a path the close never files: the .local run archive, or a record name built differently from run_state.tracked_path (lib/run_state.py:571)
- AC4 must fail on: comparing each figure's source on re-derivation, or refusing a .local source at check, either of which turns every earlier signed page INVALID
- Serves Jonah's End goal 3, 'one artefact workspace, one set of gates' (jonah-reyes-team-lead.md:28). D0461 names Graham Doyle's End goal 2 for EP0276.
- Checked at HEAD 508e2408 (2026-11-12): nothing is met yet. RPT0028.json cites `sdlc-studio/.local/run-state.json` on 267 figures, `gh run list` on 15 and `sdlc-studio/.local/refusals.jsonl, git log` on 11 (the last is US1001's). The first half of AC4 holds today by construction (sources are not digested); its second half fails until the change.
- The close derives its page with no `record` (`_file_the_report`, sprint.py:10011, build_report call at :10050-10051), so `_run_state_for` answers the live path (sprint_report.py:2931-2933).
- BG0993 already files the record at sdlc-studio/reports/runs/<RUN-ID>.json from the close onward (`_file_awaiting_record`, defined at sprint.py:9325 and called at :9874, after `_file_the_report` at :9868), so the cited path exists in the close's commit; this story re-points the citations only.
- Citing the tracked path before `_file_awaiting_record` writes it does not refuse the build: `_source_resolves` accepts any `sdlc-studio/` path, written or not (WORKSPACE_PREFIXES, sprint_report.py:4676).
- Sources are outside the fingerprint: `digest_entries` (sprint_report.py:2881-2889) digests (section, key, value) and, under TABLE_RULE, the page's price table; `fingerprint` is at :2892. A re-derivation in a fresh clone already cites the tracked record, since `_run_state_for` falls through to it (:2934-2941), so this story makes the filed page match what every clone re-derives.
- Keep `_run_state_for`'s returned read path for revalidate's tracked and archived judgements (call at sprint_report.py:5702, judgements at :5773-5774 and :5789) and for `cmd_build`'s `--write` refusal (:6070-6071); cite through a separate value set once in build_report (:4521).
- Existing tests that pin the .local citation and change with it: test_sprint_report.py:3474 (`ReportIsDerivedTests::test_figures_come_from_the_artefacts_not_the_retros_prose`, `run-state.json` in planned_units' source) and test_sprint.py:17200 (`PrepareRefusesTests::test_a_gate_clear_run_still_at_review_produces_its_report`, `run-state.json` in a close-filed page's unit_outcome source).
- reference-scripts.md:280-282 still says the run record lives in `.local/` and is not versioned, so verifying a signature needs the signing clone's record; already untrue since BG0993, and this story is where it is corrected.
- BG1007 is Superseded; the fourth criterion stands on its own as the guard that every earlier signed page still checks VALID.
- Build first in this epic: the money and lane-yield stories cite the same record. BG1010 also edits `cmd_build` and test_sprint_report.py; it fixes `run_id` only, so the two do not collide, but they share a file and land one after the other.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Persona field names Maya Okafor, but the User Story is 'As a team lead' and Notes say it serves Jonah Reyes's End goal 3 (sdlc-studio/personas/jonah-reyes-team-lead.md:24-29); either set '> **Persona:** Jonah Reyes' or record Jonah as the served Secondary, so the product seat judges it against the goal it names (D0380).
- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: line references corrected (sprint_report.py and sprint.py moved by 400 to 600 lines); Affects gains test_sprint_report.py and test_sprint.py, which pin the .local citation, and reference-scripts.md, whose run-record paragraph this makes stale; BG1007 noted Superseded; release set to 6.4 (D0461); criteria unchanged |
