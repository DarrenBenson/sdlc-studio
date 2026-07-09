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

## Findings filed (and resolved)

- **[BG0070](../bugs/BG0070-migrate-v3-build-id-map-runs-a-git.md) (High) - FIXED in this sprint.**
  `migrate_v3.build_id_map` spawned a `git log --diff-filter=A --follow -1` subprocess **per
  artefact**. First rehearsal: Project A (~1,700 files) very slow; Project B (~1,945 files)
  `build_id_map` + `migrate(dry_run)` did not complete within 150s. Fixed by batching the
  add-date lookup into a single `git log --reverse --diff-filter=A --name-only` pass.

## Re-rehearsal (after the BG0070 fix)

| Project | `build_id_map` | `migrate(dry_run)` |
| --- | --- | --- |
| Consuming project A | 0.2s (1,471 artefacts) | - |
| Consuming project B | 0.3s (1,674 artefacts) | 0.3s, migrated=1,674 |

From ">150s / did not complete" to sub-second on the same real projects.

## Outcome

The directed walk is correct and presents identically on both real projects, and the migration
now completes in well under a second on a ~1,700-artefact project. The rehearsal did its job: it
surfaced a concrete scale defect (BG0070) a fixture could not have shown, which was fixed and
re-rehearsed green in the same sprint. This is the "tested in anger" evidence for the rc-tag
checklist (US0109).
