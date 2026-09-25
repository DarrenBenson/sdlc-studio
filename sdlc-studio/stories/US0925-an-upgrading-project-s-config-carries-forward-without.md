# US0925: An upgrading project's config carries forward without the retired review keys

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, .claude/skills/sdlc-studio/reference-upgrade.md, .claude/skills/sdlc-studio/help/upgrade.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py, changelog.d/US0925.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Jonah Reyes

## User Story

**As a** team lead upgrading a consuming project to v6
**I want** `migrate` to strip or map every retired review key and Definition of Done tag, keep the opt-in settings, and report the frozen ledgers and retired verbs
**So that** the upgrade is mechanical, judgement calls are reported rather than guessed, and nothing we deleted turns into a validation error in his repo

## Acceptance Criteria

- **AC1:** Given a fixture `.config.yaml` holding every retired key (the `plan_review` block, `review.test_plan_after`, `review.plan_falsifiability`, `review.repair_plan_gate`, `review.repair_design_threshold`, `review.two_role_after`, `review.signoff`, `review.mutation_evidence`, `review.line_coverage_after`, `review.require_brief_provenance`, `quality.depth_parity_gate`), when `migrate.py --apply` runs, then each retired key's own line, and the child lines of a removed block, are removed; every other line is byte-identical, comments included; and the report names each key with what replaced it, and any comment block left directly above a removed key. Fails on: a parse-and-dump rewrite, which loses the comments and reorders keys
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_apply_strips_every_retired_key
- **AC2:** Given the same config, when `migrate.py` runs without `--apply`, then nothing is written and the report lists the same removals
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_dry_run_writes_nothing
- **AC3:** Given `review.line_coverage: block` with `review.signoff: panel`, and separately `review.signoff: operator` (the shipped value), when migrated, then `line_coverage: block` is kept unchanged and each `signoff` value is removed, the report saying the operator now signs the run once at `sprint sign`. Fails on: removing only the non-default `panel` value
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_opt_in_kept_and_panel_mapped
- **AC4:** Given a Definition of Done tagging each id in the shared retired-check-id registry (`[check: review.two-role]`, `[check: repair.mutation-evidence]`), when migrated with `--apply`, then each tag is removed, the criterion line is kept as a human-judged item, and the report names it; an id added to the registry is stripped with no change to `migrate.py`. Fails on: a second hand-kept list of ids in `migrate.py`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_retired_dod_tags_are_untagged
- **AC5:** Given the frozen ledgers present (`plan-review-verdicts.md`, `signoff-record.md`, `repair-record.md`, `critic-evidence.md`, `sprint-review-record.md`, `plan-rulings.md`), when migrated, then each is reported as frozen history and left byte-identical, and the report lists the retired scripts and verbs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_frozen_ledgers_are_reported_and_untouched
- **AC6:** Given the AC1 fixture migrated once with `--apply`, when `migrate.py --apply` runs again, then the file holds no retired key, its bytes do not change and the report lists nothing to remove. Fails on: HEAD, whose first pass strips nothing, and on a stripper that re-reports or re-writes on every pass
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_a_second_apply_is_a_no_op

## Notes

- This is new code: `migrate.py` is a 175-line orchestrator with no config or DoD rewriting today. Line-preserving removal of nested YAML keys and blocks in pure stdlib, plus tag stripping, ledger reporting and idempotence, is honestly 5 points.
- Read the retired config keys and check ids from one registry (the check ids from US0916's `RETIRED_CHECK_IDS` in `sdlc_md`), not from a list kept in `migrate.py`.
- Risk: `tools/rehearse-release.sh` drives `migrate --apply` on a v4-era workspace against `tools/release-rehearsal-baseline.txt`. Re-run the rehearsal before the tag.
- Lands after every deletion unit, and before US0926.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points (new code); AC1 removes only each key's line and a block's children, and reports orphaned comments; AC3 adds the shipped `signoff: operator`; AC4 reads the shared retired-check-id registry; rehearsal risk recorded; changelog fragment added to Affects |
