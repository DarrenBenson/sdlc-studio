# US0997: A report the close files cites the committed run record, never .local/run-state.json

> **Status:** Draft
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py, changelog.d/US0997.md
> **Epic:** EP0276
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** a team lead reviewing a teammate's sprint report from my own clone
**I want** every figure the close files from the run record, the frozen CI runs included, to cite the run record committed beside the report
**So that** each provenance link on the page opens in my clone, which never holds the closer's .local/ directory

## Acceptance Criteria

- **AC1:** Given a run closed through `sprint close`, when the filed RPT JSON is read, then every figure derived from the run record cites `sdlc-studio/reports/runs/<RUN-ID>.json`, and none cites `sdlc-studio/.local/run-state.json`, including the not-measured reasons the Markdown twin prints as the source it consulted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_close_cites_the_tracked_run_record
- **AC2:** Given a run whose CI runs the close froze on its record, when the filed page is read, then each DORA figure derived from those runs cites the tracked run record first, followed by the forge reading that filled it (`gh run list`, or its failure reason), while the figures counted from git history keep citing it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_frozen_ci_figures_cite_the_tracked_record
- **AC3:** Given that run signed with `sprint sign` and committed, when a fresh clone holding no `.local/` reads the page, then the run-record path its figures cite exists in that clone and carries the signature the page carries, and `sprint_report check` there reads VALID.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_the_cited_record_opens_in_a_fresh_clone
- **AC4:** Given a signed page whose figures cite `sdlc-studio/.local/run-state.json`, as every page filed before this change does, and a page filed after the change, when `sprint_report check` runs on each in a fresh clone, then both read VALID and only the later page cites the tracked record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_a_page_citing_local_still_checks_valid

## Notes

- Release: 6.2 (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: build_report keeps citing state_rel, the path `_run_state_for` happened to read the record from, which at a close is the live .local file
- AC2 must fail on: `_ci_runs` returning the frozen reading's own source alone (sprint_report.py:2985), so ten to fifteen DORA figures per page cite a command and no committed file
- AC3 must fail on: citing a path the close never files: the .local run archive, or a record name built differently from run_state.tracked_path
- AC4 must fail on: comparing each figure's source on re-derivation, or refusing a .local source at check, either of which turns every earlier signed page INVALID
- Serves Jonah's End goal 3, 'one artefact workspace, one set of gates' (jonah-reyes-team-lead.md:28).
- BG0993 already files the record at sdlc-studio/reports/runs/<RUN-ID>.json from the close onward (`_file_awaiting_record`, defined at sprint.py:8763 and called at :9310, after the page is filed), so the cited path exists in the close's commit; this story re-points the citations only.
- Sources are outside the fingerprint (sprint_report.py:2837 digests [section, key, value] only). The panel's probe: a re-derivation in a fresh clone already cites the tracked record on all 55 run-record figures with an identical fingerprint, so this story makes the filed page match what every clone re-derives.
- Keep `_run_state_for`'s returned read path for revalidate's tracked and archived judgements (sprint_report.py:5310 and 5326); cite through a separate value set once in build_report (sprint_report.py:4114).
- The fourth criterion is the guard BG1007's option A would need: whichever BG1007 option is ruled, this story builds first.
- Build first in this epic: the plan-digest, money and lane-yield stories cite the same record.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
