# US0925: An upgrading project's config carries forward without the retired review keys

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, .claude/skills/sdlc-studio/reference-upgrade.md, .claude/skills/sdlc-studio/help/upgrade.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Jonah Reyes

## User Story

**As a** team lead upgrading a consuming project to v6
**I want** `migrate` to strip or map every retired review key and Definition of Done tag, keep the opt-in settings, and report the frozen ledgers and retired verbs
**So that** the upgrade is mechanical, judgement calls are reported rather than guessed, and nothing we deleted turns into a validation error in his repo

## Acceptance Criteria

- **AC1:** Given a fixture `.config.yaml` holding every retired key (the `plan_review` block, `review.test_plan_after`, `review.plan_falsifiability`, `review.repair_plan_gate`, `review.repair_design_threshold`, `review.two_role_after`, `review.signoff`, `review.mutation_evidence`, `review.line_coverage_after`, `review.require_brief_provenance`, `quality.depth_parity_gate`), when `migrate.py --apply` runs, then each is removed, the report names each with what replaced it, and every other line and comment is byte-identical
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_apply_strips_every_retired_key
- **AC2:** Given the same config, when `migrate.py` runs without `--apply`, then nothing is written and the report lists the same removals
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_dry_run_writes_nothing
- **AC3:** Given `review.line_coverage: block` and `review.signoff: panel`, when migrated, then `line_coverage: block` is kept unchanged and `signoff: panel` is removed, the report saying the operator now signs the run once at `sprint sign`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_opt_in_kept_and_panel_mapped
- **AC4:** Given a Definition of Done tagging `[check: review.two-role]` or `[check: repair.mutation-evidence]`, when migrated with `--apply`, then the tag is removed, the criterion line is kept as a human-judged item, and the report names it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_retired_dod_tags_are_untagged
- **AC5:** Given the frozen ledgers present (`plan-review-verdicts.md`, `signoff-record.md`, `repair-record.md`, `critic-evidence.md`, `sprint-review-record.md`, `plan-rulings.md`), when migrated, then each is reported as frozen history and left byte-identical, and the report lists the retired scripts and verbs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_frozen_ledgers_are_reported_and_untouched
- **AC6:** Given a config migrated once, when `migrate.py --apply` runs again, then nothing changes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_a_second_apply_is_a_no_op

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
