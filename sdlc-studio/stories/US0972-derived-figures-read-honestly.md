# US0972: Derived figures read honestly

> **Status:** Ready
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_derived_figures_honest.py, changelog.d/US0972.md
> **Epic:** EP0270
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the figures the tools derive for me (a unit's files, the per-epic index, TSD staleness) to be right
**So that** I can act on them without checking each one by hand

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0592 bullets 30, 35 and 41, 3 points.

- #30 `sdlc_md.affects_files` drops extension-less root files outside a fixed list (`CODEOWNERS`, `VERSION`, `Gemfile`, `Procfile`), and the plan then says the unit declares no Affects (sprint.py:2346) rather than that its paths were not recognised. (`Node.js` is no longer read as a file at HEAD, so that half is not in scope.)
- #35 after `artifact.py batch` and `reconcile.py apply`, the story index's `Stories by Epic` table holds only its header (`changed 0 row(s)`).
- #41 `sprint.tsd_staleness` compares `git log --format=%cI` strings, so `11:00+01:00` (10:00Z) reads newer than `10:30Z`.

## Premise at HEAD

Executed at `85042135`:

```text
$ python3 -c "import sdlc_md; print(sdlc_md.affects_files('CODEOWNERS, VERSION, Gemfile'))"   # scripts/lib on sys.path
[]
```

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects line reads `CODEOWNERS, VERSION, Gemfile, Procfile`, when `sprint.py breakdown` reads it, then all four are taken as files. Fails on: HEAD `affects_files` returns `[]` for them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_derived_figures_honest.py::DerivedFiguresHonestTests::test_extensionless_root_files_are_read_as_files
- [ ] **AC2** Given a two-unit batch where one unit's every Affects token is unrecognised, when `sprint.py plan` explains its delivery mode, then it names those tokens as not recognised rather than saying the unit declares no Affects. Fails on: HEAD prints `declare no Affects` (sprint.py:2346)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_derived_figures_honest.py::DerivedFiguresHonestTests::test_dropped_tokens_are_named_not_called_absent
- [ ] **AC3** Given stories minted by `artifact.py batch` under two epics, when `reconcile.py apply` runs, then the story index's `Stories by Epic` table holds a row for every story under its epic. Fails on: HEAD leaves the table at its header and reports `changed 0 row(s)`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_derived_figures_honest.py::DerivedFiguresHonestTests::test_reconcile_fills_the_stories_by_epic_table
- [ ] **AC4** Given a fixture repository whose code was last committed at `11:00+01:00` and whose TSD at `10:30+00:00` the same day, when `sprint.tsd_staleness` reads them, then the TSD is current. Fails on: HEAD's string compare calls it stale
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_derived_figures_honest.py::DerivedFiguresHonestTests::test_staleness_compares_instants_not_strings

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
