# US0926: This repository runs on the shipped defaults with no stand-down keys

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/.config.yaml, sdlc-studio/definition-of-done.md, sdlc-studio/.version, AGENTS.md, changelog.d/US0926.md
> **Epic:** EP0263
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** operator of this repository
**I want** `migrate --apply` run on this repository to remove D0255's stand-down keys and retired check tags, with AGENTS.md, the README and the upgrade page naming no deleted gate
**So that** the repo dogfoods exactly what a consuming project gets, with no config propping up gates that no longer exist

## Acceptance Criteria

- **AC1:** Given this repository after `migrate.py --apply`, then a second `migrate.py` dry run lists no retired key, no retired `[check:]` tag and no stale `.version`; `review.line_coverage: off` is gone as equal to the shipped default; and no line of `sdlc-studio/.config.yaml`, comments included, names a key in `sdlc_md.RETIRED_CONFIG_KEYS` by its dotted path or as a YAML key. Fails on: HEAD, whose dry run lists `review.two_role_after`, `review.signoff`, `review.require_brief_provenance`, `review.line_coverage_after`, the `plan_review` block, the DoD's `[check: review.two-role]` and `.version` at 5.1.0; and `migrate --apply` alone, which keeps the comment block (lines 77-95) explaining keys nothing reads
  - **Verify:** shell python3 -c "import re,sys; sys.path.insert(0,'.claude/skills/sdlc-studio/scripts/lib'); import sdlc_md; t=open('sdlc-studio/.config.yaml').read(); bad=[k for k in sdlc_md.RETIRED_CONFIG_KEYS if re.search(r'\b'+re.escape(k)+r'\b', t) or re.search(r'(?m)^\s*#?\s*'+re.escape(k.split('.').pop())+r'\s*:', t)]; sys.exit(1 if bad else 0)" && python3 .claude/skills/sdlc-studio/scripts/migrate.py | grep -q '^migrate: 0 deterministic'
- **AC2:** Given AGENTS.md, then its review rule describes one independent reviewer per unit, briefed with `critic.py brief`, and the operator signing the run once with `sprint sign`, and it names no panel for review. Fails on: HEAD lines 83-86 ('Two roles, never merged ... a reviewer of record ... approves', read per unit) and 94 ('Resolve the panel with `persona_resolve.py panel`', whose only ceremonies are now `refine` and `triage`, so the command it points a reviewer at has no review panel)
  - **Verify:** shell ! grep -nE 'reviewer of record|persona_resolve.py panel' AGENTS.md && grep -q 'sprint sign' AGENTS.md

## Notes

- AC1 no longer conflicts with US0925's AC3: D0255 set `review.line_coverage: off` here, `migrate` keeps `line_coverage` values, and `off` becomes the default under US0922, so the key is removed by hand as redundant.
- AC2 rests on the measured premise that the Done verb never refuses a missing verdict at default config; the review bar is read in conformance and at `sprint sign`, not added to the verb.
- The orphaned comment lines in `.config.yaml` are pruned by hand here: US0925 keeps every comment byte-identical, which is right for a consuming project.
- `README.md` line 209 carries the mermaid `two-role review + sign-off` edge.
- Lands last, after US0924 and US0925.
- - 2026-09-25 (product seat census): the README half of AC3 (the mermaid `two-role review + sign-off` edge, README 209) moves to U3, which owns README.md whole; AC4 (docs/existing-users.md) moves to U4, which owns that page and its pinned test `test_existing_users_page.py`. README.md, docs/existing-users.md and test_existing_users_page.py leave this unit's Affects, so no two units edit one file. AC3 gains AGENTS.md 87-96 (the sign-off panel, retired by US0919) and 217 (`review.line_coverage` as a gate, opt-in under US0922).
- - 2026-09-27 re-measure (product seat, dee380d9): the refusal-table half of the old AC3 already holds (US0923 removed the `critic record` brief-provenance row; the table names no retired gate), so AC2 keeps only the review rule. The old AC2 (the lean path holds on the real config) is retired in the LC-002 pattern: nothing reads the retired keys any more, so stripping them changes no behaviour and the criterion cannot fail; US0950 and US0951 proved the loop on the shipped defaults. `test_lean_repo_defaults.py` is no longer needed: AC1 reads `migrate`'s own report, so no new test module is added.
- Run after BG0790, so `migrate --apply` stamps `.version` 6.0.0-rc.1 rather than 6.0.0 while this repository runs the candidate; the cut restamps 6.0.0.
- `migrate --apply` here also applies two sizing items (CR0575, CR0592: Size S from Points 3); expected, and named in the commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 2 -> 3 points; AC1 has `review.line_coverage` absent as redundant and prunes comments on retired keys; AC2 drops the false premise that Done refuses a missing verdict (the bar is read in conformance) and adds a bug so it fails at HEAD; AC3 covers the README's mermaid edge; Affects adds README.md and the changelog fragment |
| 2026-09-25 | sdlc-studio v6 planning | Product seat, Sprint 5/6 planning: README.md and docs/existing-users.md move to U3 and U4 (they own those files whole); AC4 removed and AC3 narrowed to AGENTS.md, adding its sign-off-panel and line-coverage lines; points stay 3 |
| 2026-09-27 | sdlc-studio v6 planning | Product seat, Sprint 6 re-measure at dee380d9: 3 -> 2 points; AC1 reads migrate's report (no new test module); old AC2 retired as unable to fail; old AC3 narrowed to AGENTS.md's review rule, the refusal table being already clean |
