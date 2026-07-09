# v4 migration rehearsal (US0106 / CR0198)

The "tested in anger" gate for v4.0: the v2 to v3 upgrade walk rehearsed dry-run against two
real consuming projects. Project names are redacted for neutrality; both are mature
schema-v2 projects with large artefact corpora.

> **Date:** 2026-07-09
> **Rehearsed-by:** claude (engineering seat)
> **Skill under test:** this repo's `project_upgrade.py` (with the US0106 migration walk) and
> `migrate_v3.py plan`, both read-only / dry-run. Nothing was written to either project.

## Projects

| Project | Schema | Artefact files | `project upgrade` detect |
| --- | --- | --- | --- |
| Consuming project A | v2 (behind) | ~1,705 | auto-correctable: 1, needs-judgement: 2 |
| Consuming project B | v2 (behind) | ~1,945 | auto-correctable: 2, needs-judgement: 4 |

## What was rehearsed

1. **Capability delta + directed walk.** `project upgrade --format json` on each project emits
   clean JSON and presents the ordered v2 to v3 walk: `capability delta -> migrate_v3 dry-run ->
   migrate_v3 apply -> re-baseline`. Correct on both; `detect` reports each as schema 2 / behind.
2. **`migrate_v3 plan` (dry-run).** Project A: `would migrate 1471 artefact(s) to schema v3`
   with deterministic, date-ordered ULID ids (e.g. `EP0001 -> EP-01KNAZ00`). Project B: did not
   complete (see finding below).

## Findings filed

- **[BG0070](../bugs/BG0070-migrate-v3-build-id-map-runs-a-git.md) (High).** `migrate_v3.build_id_map`
  spawns a `git log --diff-filter=A --follow -1` subprocess **per artefact**. On Project A
  (~1,700 files) the plan is very slow; on Project B (~1,945 files) `build_id_map` +
  `migrate(dry_run)` did not complete within 150s. The v4 migration path is impractical on a
  real large project until this is batched into a single git pass. **rc-relevant**: the rc-tag
  checklist (US0109) should not read green until this is resolved.

## Outcome

The directed walk itself is correct and presents identically on both real projects. The
rehearsal did its job: it surfaced a concrete scale defect (BG0070) that a fixture project
could not have shown. The migration is not yet "tested in anger green" - BG0070 must be fixed
and the plan re-rehearsed before `v4.0.0-rc.1`.
