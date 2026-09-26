# US0925: An upgrading project's config carries forward without the retired review keys

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py, .claude/skills/sdlc-studio/reference-upgrade.md, .claude/skills/sdlc-studio/help/upgrade.md, changelog.d/US0925.md, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_testplan_tooling.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_repair_plan.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Jonah Reyes

## User Story

**As a** team lead upgrading a consuming project to v6
**I want** `migrate` to strip or map every retired review key and Definition of Done tag, keep the opt-in settings, and report the frozen ledgers and retired verbs
**So that** the upgrade is mechanical, judgement calls are reported rather than guessed, and nothing we deleted turns into a validation error in his repo

## Acceptance Criteria

- **AC1:** Given a Definition of Done in the v5.1 shape, tagging `[check: review.two-role]` and `[check: repair.mutation-evidence]`, when `migrate.py --apply` runs, then each retired tag is removed, its criterion line is kept as a human-judged item, and the report names it; an id added to `sdlc_md.RETIRED_CHECK_IDS` is stripped with no change to `migrate.py`. Fails on: HEAD, where both tags survive `migrate --apply` (measured on a project initialised with v5.1.0's `init.py`); a second hand-kept list of ids in `migrate.py`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_retired_dod_tags_are_untagged
  - **Verified:** yes (2026-09-26)
- **AC2:** Given an AGENTS.md or CLAUDE.md whose text names a retired config key or verb (for example the v5.1 template's `review.two_role_after` paragraph), when `migrate.py` runs, then the report lists each such line under needs-a-human with the file and line number, and neither file is rewritten. Fails on: HEAD, which does not report the v5.1 paragraph (measured); a rewrite, which would edit a project's own instructions without judgement
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_instructions_naming_a_retired_surface_are_reported
  - **Verified:** yes (2026-09-26)
- **AC3:** Given a fixture `.config.yaml` in this repository's shape, holding retired keys set by hand (the `plan_review` block, `review.test_plan_after`, `review.two_role_after`, `review.signoff`, `review.mutation_evidence`, `review.line_coverage_after`, `review.require_brief_provenance`, `quality.depth_parity_gate`), when `migrate.py --apply` runs, then each retired key's own line and a removed block's child lines are removed, every other line is byte-identical, comments included, the report names each key with what replaced it and any comment block left directly above one, and `review.line_coverage: block` is kept. The keys are read from one registry beside `RETIRED_CHECK_IDS`. Fails on: a parse-and-dump rewrite, which loses comments and reorders keys; removing only the non-default `signoff: panel`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_apply_strips_every_retired_key
  - **Verified:** yes (2026-09-26)
- **AC4:** Given the AC1 and AC3 fixtures, when `migrate.py` runs without `--apply`, then nothing is written and the report lists the same removals; and after one `--apply`, a second changes no byte and lists nothing to remove. Fails on: a stripper that writes in dry-run, or re-reports on every pass
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_dry_run_writes_nothing_and_a_second_apply_is_a_no_op
  - **Verified:** yes (2026-09-26)
- **AC5:** Given the frozen ledgers present (`plan-review-verdicts.md`, `signoff-record.md`, `repair-record.md`, `critic-evidence.md`, `sprint-review-record.md`, `plan-rulings.md`), when migrated, then each is reported as frozen history and left byte-identical, and the report counts the `repair-record.md` and `sprint-review-record.md` rows dated on or after `critic.REPAIR_VERB_RETIRED`, saying those rows no longer answer a REJECT or cover a unit. Fails on: silence about rows the historical licence does not cover, which a v5.1 project that kept repairing after the constant would otherwise meet as a conformance finding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_frozen_ledgers_are_reported_with_their_unlicensed_rows
  - **Verified:** yes (2026-09-26)
- **AC6:** Given `migrate.py --apply` on a copy of a real consuming workspace older than v5 (a v4 consuming project's shape: schema 2, `conformance.adopt_after`, no retired key), then only `.version` changes and the conformance and validate results are identical before and after. Fails on: a stripper that touches a config holding no retired key
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_config.py::MigrateConfigTests::test_a_workspace_with_nothing_retired_is_left_alone
  - **Verified:** yes (2026-09-26)

## Notes

- This is new code: `migrate.py` is a 175-line orchestrator with no config or DoD rewriting today. Line-preserving removal of nested YAML keys and blocks in pure stdlib, plus tag stripping, ledger reporting and idempotence, is honestly 5 points.
- Read the retired config keys and check ids from one registry (the check ids from US0916's `RETIRED_CHECK_IDS` in `sdlc_md`), not from a list kept in `migrate.py`.
- Risk: `tools/rehearse-release.sh` drives `migrate --apply` on a v4-era workspace against `tools/release-rehearsal-baseline.txt`. Re-run the rehearsal before the tag.
- Lands after every deletion unit, and before US0926.
- - Re-pointed at Sprint 5 from measurement. A project initialised by v5.1.0's `init.py` holds no retired config key (its template writes only `schema_version: 3`), but its DoD carries both retired check tags and its AGENTS.md teaches `review.two_role_after`; HEAD's `migrate --apply` wrote only `.version` and left all three, and `validate` warned twice. So the DoD and AGENTS.md criteria lead, and config stripping is scoped to the hand-set shape this repository has (US0926 runs it here).
- No consuming project on this machine is on v5.x. a consuming project on 4.1.0 migrated read-only from a copy: `.version` only, conformance 0/687 and 98 not both before and after, validate 136 errors all pre-existing. AC6 pins that shape with a fixture, not the real repository.
- AC5 reads US0914's constant, so it lands after US0914 (same wave only if US0914 merges first).
- Six criteria: the old AC2 (dry-run) and AC6 (idempotence) are merged as the new AC4.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points (new code); AC1 removes only each key's line and a block's children, and reports orphaned comments; AC3 adds the shipped `signoff: operator`; AC4 reads the shared retired-check-id registry; rehearsal risk recorded; changelog fragment added to Affects |
| 2026-09-25 | sdlc-studio v6 planning | Sprint 5 grooming (engineering seat): re-pointed at the v5.1 upgrade as measured - DoD tags and AGENTS.md lead, config stripping scoped to hand-set keys, frozen-ledger report counts rows the historical licence does not cover, a no-op criterion on a real pre-v5 shape; dry-run and idempotence merged |
