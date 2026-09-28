# Upgrade rehearsal: v6 on two real projects

The rc.1 notes promised that the migration to v6 would be rehearsed on two real consuming projects
before 6.0.0, with the record linked from the 6.0.0 notes. This is that record. Fixtures prove
each upgrade step; this rehearsal proves the multi-hop path no fixture covers: schema 2, artefacts
written under v2 and v4, and around 600 stories per project.

## What ran

- **Skill:** `6.0.0-rc.1`, the scripts at commit `5e45cbf92151e36d4ef7819540e8e88b63ac159f` on
  `main` (the release candidate with its Sprint 6 fixes, including BG0785 and BG0790), run on
  2026-09-28.
- **Projects:** two consuming projects on the maintainer's machine, named here only by the skill
  version each recorded. Each was cloned into a scratch directory (committed files only); the
  originals were never written to.
- **Commands, in order, on each copy:**
  1. `migrate.py --root <copy>` (dry run), then `git status --porcelain` to prove it wrote nothing
  2. `validate.py --root <copy> check` and `gate.py --root <copy>` (the before state)
  3. `migrate.py --root <copy> --apply`
  4. `validate.py check` and `gate.py` again (the after state), then a second dry run
- **Not run:** `gate.py --release`, `verify_ac.py run` and `reconcile --verify`. One project's
  `Verify:` lines open shell sessions on live hosts, and a rehearsal must not reach them. Neither
  project has a pytest `Verify:` line, so migrate's conformance check collected no tests.

## Projects

| Project | Version before | Version after | `migrate` (dry run) | `migrate --apply` | Applied | Left to a human | `validate.py check` before / after | `gate.py` before / after |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a v4.1 project of 687 stories | 4.1.0 | 6.0.0-rc.1 | exit 0; 1 would apply, 5 for a human; 4 s | exit 0; 1 applied, 5 for a human; 5 s | the `.version` stamp (4.1.0 to 6.0.0-rc.1), one file | 5 items: 2 index drift items (the gate counts 28, BG0842); the persona index names the old two-category model; 2 AGENTS.md hygiene lines; 136 validate errors; a conformance cutoff (`adopt_after: US0784`) for 98 units (BG0845). Not named: 349 units below the engagement floor (BG0843) | exit 1 (136 errors) / exit 1 (136 errors) | exit 1 / exit 1 |
| a v2.4 project of 593 stories, with frozen sign-off records | 2.4.1 | 6.0.0-rc.1 | exit 0; 46 would apply, 18 for a human; 7 s | exit 0; 46 applied, 18 for a human; 7 s | the `.version` stamp (2.4.1 to 6.0.0-rc.1) and a `Size:` line on 36 change requests and 9 epics converted from legacy Points or Effort, 46 files | 18 items: no seat covers engineering, QA or product (`persona generate --team` offered); nested `team/` and `stakeholders/` persona folders; 3 AGENTS.md hygiene lines; 562 validate errors; 12 accepted requests never decomposed, each with its `refine` command; 1 bug sized in legacy Effort; a conformance cutoff for 1 unit (US0601). Left as written: the two frozen ledgers `signoff-record.md` and `sprint-review-record.md` | exit 1 (562 errors) / exit 1 (562 errors) | exit 1 / exit 1 |

The story counts are story files, not counting the index. Both projects went through the upgrade
without error, and neither dry run wrote a byte: `git status` was empty after each. Both second
dry runs reported nothing left to apply and the same human list, so the apply is idempotent. The
`validate.py check` error set was identical before and after on both projects: migrate introduced
no validation error. Each migrate run took under 10 seconds.

### Reading the gate columns

`gate.py` stayed red on both projects, as it was before the upgrade, and the lanes that failed
changed for a reason that is not the upgrade. On a clean tree the gate judges the whole workspace;
on a tree with changes it judges only the changed artefacts. So the lanes it scopes read
differently depending on what `--apply` touched:

- **v4.1, before:** conformance (98 units), reconcile (28 items), validate (136 errors) and the
  engagement floor (349 units) failed. **After:** reconcile and the engagement floor still failed.
  Conformance and validate passed, because the diff held one file, `.version`. Once the upgrade
  is committed the tree is clean again and both lanes judge, and fail, the whole workspace.
- **v2.4, before:** conformance (1 unit) and validate (562 errors) failed. **After:** validate
  failed on 28 errors in the 45 artefacts the sizing conversion touched. Those errors were already
  there: the validate error set did not change.

Read the migrate report, not the gate's post-apply lanes, for what the project owes: the report
counts the whole workspace every time.

One more side effect: the first `gate.py` run wrote `sdlc-studio/.local/gate-cost.json`. The v4.1
project does not ignore that file. The v2.4 project has committed its `.local/` folder, so every
gate run changes a tracked file there (BG0844).

## Findings

Every defect the rehearsal found is filed. None is High, so none blocks the 6.0.0 cut; each ships
disclosed.

| # | Finding | Severity | Owner |
| --- | --- | --- | --- |
| 1 | migrate reports 2 index drift items where the gate's reconcile lane fails on 28: the upgrade counts two of reconcile's nine drift sources | Medium | BG0842 |
| 2 | migrate names no engagement-floor cutoff, so the v4.1 project's 349 units below the floor surface only at the gate | Medium | BG0843 |
| 3 | an upgraded project never gets the `sdlc-studio/.gitignore` that `init` writes, so gate runs leave runtime state in `git status` | Medium | BG0844 |
| 4 | the proposed conformance cutoff exempts the 98 units after the project's own cutoff: 49 hold an APPROVE row in the v4.1 ledger shape, which has no Author column and so never reads as independent; the report also says "add" for a key the project already sets | Medium | BG0845 |

## What an upgrader should expect

- `migrate` then `migrate --apply` is safe to run: the dry run writes nothing, the apply writes
  only the version stamp and sizing lines, and a second run finds nothing more to apply.
- The needs-a-human list is the work. On a v2.4 project most of it is persona layout, seats and
  undecomposed requests. On a v4.1 project it is the conformance cutoff, which needs judgement
  (BG0845).
- The gate is red after the upgrade on a busy older project. Judge it from the whole workspace,
  after committing the upgrade, and expect the engagement floor and reconcile to need attention
  beyond what the report names (BG0842, BG0843).
