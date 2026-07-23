# US0354: conformance and validate gain a diff-scoped mode over touched artefacts plus global census and link checks, release gate stays whole-workspace

> **Status:** Draft
> **Delivers:** CR0344
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0121
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py,.claude/skills/sdlc-studio/scripts/validate.py,.claude/skills/sdlc-studio/scripts/gate.py,.claude/skills/sdlc-studio/help/gate.md,.claude/skills/sdlc-studio/scripts/tests/test_conformance.py,.claude/skills/sdlc-studio/scripts/tests/test_validate.py,.claude/skills/sdlc-studio/scripts/tests/test_gate.py

## User Story

**As a** committer whose workspace carries an in-flight backlog of ungroomed or
part-built units
**I want** the blocking conformance and validate lanes to judge only the artefacts
my commit touches, while the repo-wide census, index and link checks keep running
over everything
**So that** a commit that changes nothing about the pre-existing debt is not held
hostage by it, and the pressure to reach for `--no-verify` - which disarms every
lane, not just the noisy two - goes away

## Acceptance Criteria

### AC1: validate judges only the changed artefacts while the repo-wide sweeps still run

- **Given** a workspace where one artefact in the diff is well-formed and a second,
  untouched artefact carries a validation error
- **When** `validate.py check --changed` runs
- **Then** it exits 0: the per-file lane covers only the diff's artefacts, while
  `excluded_id_files` and `check_dor_dod` still run over the whole tree, and the
  untouched error is printed as an advisory line rather than counted in the exit code
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::DiffScopedCheckTests::test_untouched_error_is_advisory_while_global_sweeps_still_run

### AC2: conformance judges only the touched units, and a repo-global stage still blocks

- **Given** a workspace with a non-conformant story outside the diff and a failing
  repo-global stage (doc-coverage or a missing story index)
- **When** `conformance.py check --changed` runs
- **Then** the untouched unit is reported but excluded from the `nonconformant`
  count that decides the exit code, while `global_failures` is still counted and
  still fails the command - narrowing the per-unit scope must not disarm the
  repo-wide stages
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::DiffScopedConformanceTests::test_untouched_unit_is_advisory_but_a_global_stage_still_fails

### AC3: the pre-commit gate scopes both lanes, the release gate stays whole-workspace

- **Given** the same workspace, with the debt entirely outside the commit's diff
- **When** `gate.py` runs in its plain pre-commit form and then again with `--release`
- **Then** the plain run reports the `conformance` and `validate` lanes green (the
  debt named in their detail text as advisory) while the `--release` run reports both
  lanes failing over the whole workspace, from one code path with no second set of
  rules
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DiffScopedLaneTests::test_precommit_scopes_the_lanes_and_release_keeps_them_whole_workspace

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
