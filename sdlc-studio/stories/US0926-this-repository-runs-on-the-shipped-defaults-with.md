# US0926: This repository runs on the shipped defaults with no stand-down keys

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/.config.yaml, sdlc-studio/definition-of-done.md, AGENTS.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py, changelog.d/US0926.md
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator of this repository
**I want** `migrate --apply` run on this repository to remove D0255's stand-down keys and retired check tags, with AGENTS.md, the README and the upgrade page naming no deleted gate
**So that** the repo dogfoods exactly what a consuming project gets, with no config propping up gates that no longer exist

## Acceptance Criteria

- **AC1:** Given this repository after `migrate.py --apply`, then `sdlc-studio/.config.yaml` holds none of the retired keys; `review.line_coverage` is absent (it equalled the new default `off`); no comment names a retired key except to say it is retired; and `sdlc-studio/definition-of-done.md` carries no retired check tag. Fails on: running `migrate` alone, which keeps comments byte-identical and so leaves about 60 comment lines explaining keys that no longer exist
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py::RepoDefaultsTests::test_the_repo_config_holds_no_retired_key
- **AC2:** Given a mirror of this repository on the stripped config, when a story and a bug, each with green criteria and an independent delivery APPROVE and the bug with no `Verification depth`, are moved to Done and Fixed, then each succeeds with no plan review, test plan, sign-off, depth or mutation evidence asked for; and the same story with no verdict reads critiqued unmet in `conformance.py check`. Fails on: HEAD's config, under which the bug is refused for its missing depth tier
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py::RepoDefaultsTests::test_the_lean_path_holds_on_the_real_config
- **AC3:** Given AGENTS.md, then its refusal table names no retired gate (brief provenance on `critic record`, `critic signoff`, `Verification depth` on `transition -> Fixed`, the two-role rule on `transition -> Done`), its lane roster names no deleted lane (`derived-depth`, `evidence-drift`), its review rule points at no retired sign-off panel (`persona_resolve.py panel` for review), and its soft-dependency table does not describe `review.line_coverage` as a gate. Fails on: HEAD (AGENTS.md 50, 51, 87-96, 217)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py::RepoDefaultsTests::test_agents_md_names_no_retired_gate

## Notes

- AC1 no longer conflicts with US0925's AC3: D0255 set `review.line_coverage: off` here, `migrate` keeps `line_coverage` values, and `off` becomes the default under US0922, so the key is removed by hand as redundant.
- AC2 rests on the measured premise that the Done verb never refuses a missing verdict at default config; the review bar is read in conformance and at `sprint sign`, not added to the verb.
- The orphaned comment lines in `.config.yaml` are pruned by hand here: US0925 keeps every comment byte-identical, which is right for a consuming project.
- `README.md` line 209 carries the mermaid `two-role review + sign-off` edge.
- Lands last, after US0924 and US0925.
- - 2026-09-25 (product seat census): the README half of AC3 (the mermaid `two-role review + sign-off` edge, README 209) moves to U3, which owns README.md whole; AC4 (docs/existing-users.md) moves to U4, which owns that page and its pinned test `test_existing_users_page.py`. README.md, docs/existing-users.md and test_existing_users_page.py leave this unit's Affects, so no two units edit one file. AC3 gains AGENTS.md 87-96 (the sign-off panel, retired by US0919) and 217 (`review.line_coverage` as a gate, opt-in under US0922).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 2 -> 3 points; AC1 has `review.line_coverage` absent as redundant and prunes comments on retired keys; AC2 drops the false premise that Done refuses a missing verdict (the bar is read in conformance) and adds a bug so it fails at HEAD; AC3 covers the README's mermaid edge; Affects adds README.md and the changelog fragment |
| 2026-09-25 | sdlc-studio v6 planning | Product seat, Sprint 5/6 planning: README.md and docs/existing-users.md move to U3 and U4 (they own those files whole); AC4 removed and AC3 narrowed to AGENTS.md, adding its sign-off-panel and line-coverage lines; points stay 3 |
