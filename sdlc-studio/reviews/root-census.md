# Root resolution census

> **Created:** 2026-07-24
> **Created-by:** sdlc-studio
> **Scope:** every `*.py` in `.claude/skills/sdlc-studio/scripts/`

Every script in the family is classified by how it turns `--root` into the project it
operates on. The classification is measured, not asserted: a script declares `--root` when
its parser or its source says so, and it counts as anchored only when a `resolve_root` call
site in it binds the shared implementation in `lib/sdlc_md.py`, checked by object identity.
`tests/test_root_census.py` re-measures on every run and holds this record to the result, so
a script added to the family with no row here fails the suite - it cannot join unclassified -
and a row claiming an anchor the script does not have fails too.

Three classifications, one per script:

- **anchored** - resolves through the shared resolver, so a run from any directory reaches
  the same workspace.
- **unanchored** - takes the family default `.` as the cwd. A run from a subdirectory then
  reads an empty tree, or writes into a stray one beside the cwd, and exits 0. Every entry
  names the follow-up that tracks it; silence is not a classification.
- **non-root** - deliberately has no project-root surface, with the reason stated.

The measured limit, stated rather than glossed: the unit is the SCRIPT, not the call site. A
script counts as anchored once one call site binds the shared resolver, so one converted
verb sitting beside two bare ones reads as anchored here. A mutation run confirmed it -
reverting a single verb of `next_id.py` left the classification unchanged, and only
reverting all three moved it. Per-verb coverage is what the follow-up has to carry.

## Measured 2026-07-24

| Classification | Scripts |
| --- | --- |
| anchored | 5 |
| unanchored | 59 |
| non-root | 5 |
| **total** | **69** |

Of the 59 unanchored, 26 write and 33 only read; the writers are the fail-open half and
should be repaired first. `next_id.py` was fixed ahead of the rest because it is the
collision case: an allocator reading an empty tree hands back an id the real workspace
already holds.

## Census

| Script | Classification | Reason or follow-up |
| --- | --- | --- |
| `ac_scope.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `archive.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `artifact.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `audit.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `audit_check.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `audit_cost.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `autosprint.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `backfill_authorship.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `backlog_triage.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `blocker_sweep.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `carry_forward.py` | non-root | library module with no CLI surface; its caller passes the resolved root |
| `changelog.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `close_owed.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `command_audit.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `complexity.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `config.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `conformance.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `constitution.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `critic.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `decisions.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `deploy.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `digest.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `disclosure.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `doc_coverage.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `doc_freshness.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `engagement_floor.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `file_finding.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `flow.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `gate.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `github_sync.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `handoff.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `init.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `integrity.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `ledger.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `lessons.py` | anchored | resolves through `sdlc_md.resolve_root` |
| `lite_profile.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `loop_guard.py` | anchored | resolves through `sdlc_md.resolve_root` |
| `migrate.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `migrate_v3.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `mutation.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `next_id.py` | anchored | resolves through `sdlc_md.resolve_root` |
| `persona_gen.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `persona_resolve.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `plan.py` | non-root | operates on the operator's `~/.claude/plans/` tree, which sits outside any project |
| `plan_review.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `project_upgrade.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `provenance.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `pvd.py` | non-root | operates on a `--master` and a `--target` repo, so no single project root applies |
| `reconcile.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `refine.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `repair_plan.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `repo_map.py` | anchored | resolves through `sdlc_md.resolve_root` |
| `resume.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `retro.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `review_prep.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `rfc.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `route.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `spec_guard.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `sprint.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `sprint_report.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `status.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `telemetry.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `transition.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `triage.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `triage_noise.py` | non-root | library module with no CLI surface; its caller passes the resolved root |
| `triage_sampling.py` | non-root | library module with no CLI surface; its caller passes the resolved root |
| `validate.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
| `verify_ac.py` | anchored | resolves through `sdlc_md.resolve_root` |
| `version_check.py` | unanchored | takes the default `.` as the cwd; tracked by BG0282 |
