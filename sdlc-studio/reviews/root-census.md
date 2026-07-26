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
and a row that disagrees with the measurement in EITHER direction fails too.

Three classifications, one per script:

- **anchored** - resolves through the shared resolver, so a run from any directory reaches
  the same workspace.
- **unanchored** - takes the family default `.` as the cwd. A run from a subdirectory then
  reads an empty tree, or writes into a stray one beside the cwd, and exits 0. Every entry
  names the follow-up that tracks it; silence is not a classification.
- **non-root** - deliberately has no project-root surface, with the reason stated. The reason
  is itself held to the code: a row claiming no CLI must define no `main`, a row claiming a
  `--help` stub must define one and dispatch to nothing, and a row naming a path option must
  name one the script actually declares.

## What the measurement can and cannot see

The unit is the SCRIPT, not the call site. A script counts as anchored once one call site
binds the shared resolver, so one converted verb sitting beside two bare ones would read as
anchored here. A mutation run confirmed it - reverting a single verb of `next_id.py` left the
classification unchanged, and only reverting all three moved it.

**A call site is not an anchor**, and this census was wrong about that twice. The closing
review found five scripts passing on a call made for the mutation guard while every verb still
wrote through a bare `--root`: `artifact.py` - the creator this project mandates - minted into a
stray `sdlc-studio/` beside the cwd when run from a subdirectory, with an id the real workspace
already held, and exited 0.

`tests/test_root_anchor_contract.py` is the answer to that, and it is the stronger instrument of
the two. It calls each script's `main()` with a namespace it owns, from a subdirectory of a
fixture project, and asserts on the value the DISPATCH receives rather than on the presence of a
call. A resolver call made for a guard no longer stands in for an anchor. It also holds the other
half of the contract: a root the caller NAMED is honoured verbatim, so anchoring only ever widens
the default `.` and never retargets an explicit `--root X`.

The census remains the coarser view, kept because it is the one that enumerates: it is how a
script joins the family classified rather than silently.

## Measured 2026-07-24 (after the anchoring sweep)

| Classification | Scripts |
| --- | --- |
| anchored | 64 |
| unanchored | 1 |
| non-root | 5 |
| **total** | **70** |

These counts are now PARSED by the guard and held to the measurement. They were not before, which
is how the block came to claim 5 anchored / 59 unanchored while the family measured otherwise: a
sibling branch landed the resolver in five more scripts, nothing re-measured, and the guard waived
every stale row as "stale, not false". Both holes are closed - the counts are checked, and a row
that disagrees with the measurement fails whichever way it disagrees.

The one remaining `unanchored` row is `autosprint.py`, which has no `main` of its own: it
re-exports `sprint.main` verbatim. It is anchored in behaviour - the contract suite calls it and
it passes - but the census reads call sites in a script's own source and cannot see through a
re-export.

## Census

| Script | Classification | Reason or follow-up |
| --- | --- | --- |
| `ac_scope.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `archive.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `artifact.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `readiness.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `schema_check.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `audit_cost.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `autosprint.py` | unanchored | anchored in behaviour through `sprint.main`, which it re-exports verbatim; the measurement reads call sites in a script's OWN source and cannot see through a re-export, so it reads unanchored here. Measured and covered by BG0288 - the anchor-contract suite calls its `main` and it passes |
| `backfill_authorship.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `backlog_triage.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `blocker_sweep.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `carry_forward.py` | non-root | library module with no CLI at all; its caller passes the resolved root |
| `changelog.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `close_owed.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `command_audit.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `complexity.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `config.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `conformance.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `constitution.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `critic.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `decisions.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `deploy.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `digest.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `disclosure.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `doc_coverage.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `doc_freshness.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `engagement_floor.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `file_finding.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `flow.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `gate.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `github_sync.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `handoff.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `init.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `integrity.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `ledger.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `lessons.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `lite_profile.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `loop_guard.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `migrate.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `migrate_v3.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `mutation.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `next_id.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `persona_gen.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `persona_resolve.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `plan.py` | non-root | operates on the operator's `~/.claude/plans/` tree via `--plans-dir`, which sits outside any project |
| `plan_review.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `project_upgrade.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `provenance.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `pvd.py` | non-root | operates on a `--master` and a `--target` repo, so no single project root applies |
| `reconcile.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `refine.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `release_cut.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `repair_plan.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `repo_map.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `resume.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `retro.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `review_prep.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `rfc.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `route.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `spec_guard.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `sprint.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `sprint_report.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `status.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `telemetry.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `transition.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `triage.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `triage_noise.py` | non-root | library module whose only surface is a `--help` stub with no verbs behind it; its caller passes the resolved root |
| `triage_sampling.py` | non-root | library module whose only surface is a `--help` stub with no verbs behind it; its caller passes the resolved root |
| `validate.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `verify_ac.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
| `version_check.py` | anchored | resolves through `sdlc_md.resolve_root` and writes the value back onto `args` in `main`, so every verb receives it |
