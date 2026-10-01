# US0978: The handoff writers and the require-handoff gate are retired; old handoff files stay readable

> **Status:** Ready
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/help/handoff.md, .claude/skills/sdlc-studio/help/help.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0268
> **Delivers:** CR0590
> **Depends on:** US0967
> **Persona:** Maya Okafor
> **Points:** 3

## User Story

**As a** solo founder-engineer running sprints (Maya)
**I want** the handoff page's writers, template and gate retired once the signed report carries the handed-over work
**So that** a run ends with one page, and no command still writes or demands the page it replaced

## Acceptance Criteria

- [ ] **AC1** Given the shipped CLIs, when `gate.py --require-handoff HO0001` and `artifact.py new --type handoff --title x --dry-run` run, then both exit 2 as unknown, `handoff.py --help` lists no `generate` verb, and `reference-sprint.md` names no handoff the close writes. Fails on: HEAD accepts `--require-handoff` (gate.py:2803), `artifact.py new --type handoff --dry-run` would create HO-0094, and reference-sprint.md:187 reads "The close writes a handoff for every run"
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py::ReportReplacesHandoffTests::test_the_handoff_writers_and_gate_are_retired
- [ ] **AC2** Given a fixture holding an HO file and its `handoffs/_index.md` row from before this change, when `reconcile.py detect` runs, then it exits 0 reporting no handoff drift and both files are byte-identical afterwards. Fails on: a deletion that drops `handoff` from `sdlc_md.ARTIFACT_TYPES`, which orphans the 94 HO files already in this repository
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py::ReportReplacesHandoffTests::test_old_handoffs_stay_readable_and_unrewritten

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | sprint planning | Split from US0967 at the 8-point ceiling: its AC4 and AC5 (retire the handoff writers and gate; old handoff files stay readable), on the operator-approved sprint. |
