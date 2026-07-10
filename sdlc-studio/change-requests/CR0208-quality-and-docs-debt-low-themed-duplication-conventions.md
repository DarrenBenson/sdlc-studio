# CR-0208: quality and docs debt (Low, themed): duplication, conventions, doc accuracy and DX items from RV0007

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

Consolidated Low quality/doc findings from RV0007 (each verified; one artefact per the filing protocol). Items: (1) duplication/dead code lib should own (reconcile._row_counts == _canonical_counts :412/:601; artifact._schema_v3 vs sdlc_md.is_schema_v3; next_id._origin_default_branch == sprint._default_branch; three near-identical header-pinned loops in reconcile; dead `sdlc_md.METADATA_FIELD_RE`, `reconcile._SEP_LINE_RE`/`_is_sep_line`); (2) complexity hotspots regrown post-US0103 (sprint.cmd_plan cognitive 72, github_sync.cmd_push 66, reconcile._index_rows_and_summary 47, _insert_missing_summary_rows 45, telemetry.summarise 45; 91 functions over the repo's own cognitive-15 line); (3) no code-fence awareness in sdlc_md.iter_tables / verify_ac.parse_story (fenced example Verify lines execute, fenced tables tallied); (4) pre-commit hook runs the suites only when scripts/ or tools/ staged though tests assert over templates/ (.githooks/pre-commit:108); (5) git-invoking tests do not neutralise host config - gpgsign workstations fail ~8 files (test_gate.py:399 et al; set GIT_CONFIG_GLOBAL=/dev/null); (6) anchor-doc numeric drift (LATEST.md '1457 tests' vs 1455 measured; AGENTS.md 42/31 file counts vs 51/39; trd.md self-contradicts 42-vs-46 reference files, '~195-line' SKILL.md vs 253, 72-vs-73 templates); (7) private-underscore cross-module use + reconcile hub at 14 importers (reconcile._DEFAULT_TYPES <- migrate_v3/constitution/gate; _index_row_ids <- next_id; sdlc_md._b32 <- migrate_v3); (8) the five CR0200 reference-scripts-*.md split pages are disclosure orphans and 10 scripts lack the executable bit trd.md:197 mandates; (9) exit-code drift: spec_guard.py:112 and plan_review.py:234 return 2 (and plan_review :69 returns 5) where the family returns 1 on check-failure and argparse owns 2; (10) --format json missing on eight newer report verbs (github_sync incl. status, plan_review, spec_guard, loop_guard, ledger, critic, doc_freshness, persona_resolve); (11) test stdout leaks around the unittest summary (agent-instructions/check_versions prints); (12) review_generate scan takes the raw secret as argv (CWE-214; add --secret-env/stdin); (13) `conventions._TITLE_ID_RE` requires 3-4 digits so a ULID-titled artefact without a Status line silently drops from the census; (14) `_master_data_header` 3-way tie-break compares only first/last winners (reconcile.py:866-875); (15) consolidation CR slug doubles the theme ('low-severity-low-severity-...', triage_noise.py:115/:186); (16) provenance-tag guard misses scripts/lib/*.py and templates/**/*.md - live leaks at sdlc_md.py:200/207/218/357/462/619/643 and the amigo seat cards (US0111 gap); (17) check_links.py never scans root docs and skips anchor-less links (tools/check_links.py:24,:31); (18) SECURITY/help drift set: help/arguments.md:63 --goal 'done or design' vs the four-rung ladder, help/references.md omits reference-outputs.md + the five split pages and still advertises removed archetypes, trd 'visualise' vs 'containerize' spelling, INSTALL.md:57-vs-76 self-contradiction on ~/.agents/skills readers, install.sh --help values line omits agents; (19) eval scenario coverage frozen at the four v2.0.0 scenarios - nothing guards schema-v3 init, the upgrade walk, sprint rungs or the independence gate; (20) --target auto with gh on PATH writes ./.github/skills into the cwd on a global install (install.sh:148,:393-396).

## Acceptance Criteria

- [ ] Duplicates folded into lib/sdlc_md.py and dead regexes deleted
- [ ] cmd_plan and cmd_push decomposed under the cognitive-15 line; reconcile writers fall out of the status-bleed fix
- [ ] iter_tables/parse_story skip fenced blocks
- [ ] Hook suite-trigger regex includes templates/; a shared test helper neutralises host git config
- [ ] One doc pass reconciles LATEST/AGENTS/trd counts (prefer computed or ranged figures); help/references regenerated from disk; SECURITY-adjacent help drift corrected
- [ ] Private cross-module names promoted to public; provenance guard covers scripts/lib and templates/**.md with leaks stripped
- [ ] check_links gains a root-docs pass and anchor-less file-exists checks
- [ ] spec_guard/plan_review return 1 on check-failure; --format json added to the eight report verbs; test stdout captured
- [ ] review_generate scan accepts --secret-env/stdin; `_TITLE_ID_RE` accepts ULID ids; tie-break compares all winners; consolidation slug de-duplicated
- [ ] At least two new eval scenarios cover v4 surfaces; --target auto excludes copilot on global scope

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Raised |
