# Bug Index

**Last Updated:** 2026-07-04

## Summary

| Status | Count |
| --- | --- |
| Open | 0 |
| In Progress | 0 |
| Fixed | 0 |
| Verified | 0 |
| Closed | 49 |
| Won't Fix | 0 |
| Superseded | 0 |
| **Total** | **49** |

## All Bugs

| ID | Title | Status | Severity | Created | Updated |
| --- | --- | --- | --- | --- | --- |
| [BG0001](BG0001-workflow-cr-status-vocabulary-diverges-across-refe.md) | Workflow/CR status vocabulary diverges across reference table, status-flow diagram, and sdlc_md.py code | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0002](BG0002-reconcile-py-and-status-py-both-omit-bug-and-workf.md) | reconcile.py and status.py both omit bug and workflow artifact types from their deterministic census | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0003](BG0003-verify-ac-py-only-parses-ac-headings-silently-igno.md) | verify_ac.py only parses ### AC headings, silently ignoring the bullet AC style the rest of the skill accepts, so the release gate passes vacuously | Closed | Critical | 2026-06-20 | 2026-06-20 |
| [BG0004](BG0004-review-prep-persona-check-reads-personas-md-while.md) | review_prep persona check reads personas.md while the epic cascade reads personas/ directory, so the persona-usage leg silently no-ops | Closed | Medium | 2026-06-20 | 2026-06-20 |
| [BG0005](BG0005-prd-performance-nfr-falsely-claims-all-scripts-are.md) | PRD Performance NFR falsely claims all scripts are read-only over the workspace | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0006](BG0006-prd-names-its-own-artifact-metadata-format-two-inc.md) | PRD names its own artifact metadata format two incompatible ways (YAML frontmatter vs blockquote headers) | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0007](BG0007-prd-quality-assessment-conceals-four-open-bugs-inc.md) | PRD Quality Assessment conceals four open bugs (incl. a Critical) while overclaiming feature completeness | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0008](BG0008-trd-script-contract-rule-5-is-incomplete-verify-ac.md) | TRD script contract rule 5 is incomplete: verify_ac and lessons.py write outside the stated 'single exception' | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0009](BG0009-trd-181-script-layer-tests-all-must-pass-before-re.md) | TRD '181 script-layer tests, all must pass before release' gate fails in the installed copy | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0010](BG0010-tsd-instruction-hygiene-release-gate-validate-py-i.md) | TSD instruction-hygiene release gate (validate.py instructions) is wired into no CI or npm script | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0011](BG0011-tsd-availability-gate-is-inverted-the-cited-test-p.md) | TSD Availability gate is inverted: the cited test proves a hard abort (exit 127), not graceful degradation | Closed | Medium | 2026-06-20 | 2026-06-20 |
| [BG0012](BG0012-tsd-lint-links-gate-is-skill-scoped-so-the-sdlc-st.md) | TSD lint:links gate is skill-scoped, so the sdlc-studio/ artifact corpus is never link-checked (25 broken anchors slip through) | Closed | Medium | 2026-06-20 | 2026-06-20 |
| [BG0013](BG0013-persona-section-headings-carry-a-high-suffix-that.md) | Persona section headings carry a [HIGH] suffix that breaks every story anchor and the review_prep persona-usage oracle | Closed | Medium | 2026-06-20 | 2026-06-20 |
| [BG0014](BG0014-story-verify-lines-do-not-test-what-their-acs-asse.md) | Story Verify lines do not test what their ACs assert: broken shell expressions, regex-metachar failures, and source-grep smoke tests | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0015](BG0015-epic-ownership-double-mapping-github-sync-review-p.md) | Epic ownership double-mapping: github_sync, review_prep and next_id are each claimed by two epics | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0016](BG0016-ep0004-s-prd-reference-points-to-section-10-with-a.md) | EP0004's PRD Reference points to section 10 with a non-existent 'Validation Requirement' link text | Closed | Low | 2026-06-20 | 2026-06-20 |
| [BG0017](BG0017-rfc0003-buries-a-fixable-false-guarantee-reconcile.md) | RFC0003 buries a fixable false-guarantee (reconcile 'Idempotent') inside an unsettled RFC, so the wrong doc stays uncorrected | Closed | Medium | 2026-06-20 | 2026-06-20 |
| [BG0018](BG0018-reconcile-index-status-parser-matches-title.md) | reconcile index-status parser matches a status word in the title column | Closed | Medium | 2026-06-20 | 2026-06-20 |
| [BG0019](BG0019-determinism-checks-mishandle-bug-artifact-class.md) | integrity and audit mishandle the bug artifact class | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0020](BG0020-parser-rejects-consuming-repo-house-templates.md) | shared parser rejects consuming repos' house templates | Closed | High | 2026-06-20 | 2026-06-20 |
| [BG0021](BG0021-escaped-pipe-split-other-parsers.md) | escaped-pipe split bug present in three more table parsers | Closed | Medium | 2026-06-20 | 2026-06-20 |
| [BG0022](BG0022-artifact-new-silent-wiring-to-a-non-existent.md) | artifact new - silent wiring to a non-existent epic and file-only id allocation | Closed | Medium | 2026-06-21 | 2026-06-21 |
| [BG0023](BG0023-critic-verdict-text-with-underscored-identifiers-trips-markdownlint.md) | critic verdict text with underscored identifiers trips markdownlint MD037 | Closed | Low | 2026-06-21 | 2026-06-21 |
| [BG0024](BG0024-version-check-serves-stale-cached-latest-older-than.md) | version_check serves stale cached latest older than installed reports up-to-date wrongly | Closed | Medium | 2026-06-21 | 2026-06-21 |
| [BG0025](BG0025-project-upgrade-dry-run-omits-the-stale-version.md) | project_upgrade dry-run omits the stale .version bump that --apply performs | Closed | Medium | 2026-06-21 | 2026-06-21 |
| [BG0026](BG0026-reconcile-count-block-rewrite-stamps-global-total-into.md) | reconcile count-block rewrite stamps global total into per-epic count sub-tables | Closed | High | 2026-06-22 | 2026-06-22 |
| [BG0027](BG0027-persona-checks-flag-non-persona-files-and-review.md) | persona checks flag non-persona files and review-seat charters as old/ill-formed | Closed | Medium | 2026-06-22 | 2026-06-22 |
| [BG0028](BG0028-verify-ac-shells-out-prose-verify-lines-and.md) | verify_ac shells out prose Verify lines and times out reporting failed not manual | Closed | Medium | 2026-06-22 | 2026-06-22 |
| [BG0029](BG0029-project-upgrade-apply-bundles-reconcile-no-granular-flag.md) | project upgrade apply bundles reconcile no granular flag can corrupt indexes | Closed | High | 2026-06-22 | 2026-06-22 |
| [BG0030](BG0030-project-upgrade-version-bump-drops-existing-created-at.md) | project upgrade version bump drops existing created_at field | Closed | Medium | 2026-06-22 | 2026-06-22 |
| [BG0031](BG0031-reconcile-apply-auto-deletes-orphan-rows-destroying-inline.md) | reconcile apply auto-deletes orphan rows destroying inline-only records | Closed | High | 2026-06-22 | 2026-06-22 |
| [BG0032](BG0032-reconcile-reads-fixed-status-column-misreads-multi-schema.md) | reconcile reads fixed status column misreads multi-schema index tables | Closed | High | 2026-06-22 | 2026-06-22 |
| [BG0033](BG0033-five-moderate-npm-dependency-vulnerabilities-via-markdownlint-cli.md) | five moderate npm dependency vulnerabilities via markdownlint-cli | Closed | Medium | 2026-06-22 | 2026-06-22 |
| [BG0034](BG0034-sprint-plan-silently-selects-an-empty-batch-for.md) | sprint plan silently selects an empty batch for lowercase --crs/--bugs/--stories status args | Closed | high | 2026-06-24 | 2026-06-24 |
| [BG0035](BG0035-duplicate-id-gate-false-positives-on-the-canonical.md) | duplicate-id gate false-positives on the canonical two-table story index (per-epic + All Stories) | Closed | high | 2026-06-24 | 2026-06-24 |
| [BG0036](BG0036-init-creates-sdlc-studio-local-but-no-gitignore.md) | init creates sdlc-studio/.local but no .gitignore, so consuming projects commit runtime caches/reports | Closed | medium | 2026-06-24 | 2026-06-24 |
| [BG0037](BG0037-verify-ac-run-story-overwrites-the-whole-verify.md) | verify_ac run --story overwrites the whole verify-report.json instead of merging, breaking the Done-gate for batch sprints | Closed | high | 2026-06-24 | 2026-06-24 |
| [BG0038](BG0038-integrity-requires-a-story-link-on-test-specs.md) | integrity requires a Story link on test-specs, breaking epic-scoped test-specs | Closed | high | 2026-06-25 | 2026-06-25 |
| [BG0039](BG0039-adoption-cutoff-config-is-inconsistent-across-gates-and.md) | adoption cutoff config is inconsistent across gates and silently fails | Closed | high | 2026-06-25 | 2026-06-25 |
| [BG0040](BG0040-validate-personas-reports-well-formed-when-personas-are.md) | validate personas reports well-formed when personas are nested | Closed | medium | 2026-06-25 | 2026-06-25 |
| [BG0041](BG0041-old-persona-model-detector-is-name-based-and.md) | old-persona-model detector is name-based and its remediation hint misdirects | Closed | medium | 2026-06-25 | 2026-06-25 |
| [BG0042](BG0042-persona-resolve-ignores-existing-review-seats-so-authored.md) | persona_resolve ignores existing review seats so authored seats are shadowed by generic defaults | Closed | high | 2026-06-25 | 2026-06-25 |
| [BG0043](BG0043-reconcile-apply-drops-bold-markup-cr-index-row.md) | reconcile apply drops bold-markup CR-index row statuses and skips the CR-summary recompute | Closed | medium | 2026-06-25 | 2026-06-25 |
| [BG0044](BG0044-reconcile-flattens-per-epic-done-count-blocks-corrupting.md) | reconcile flattens per-epic Done count blocks corrupting per-section sub-tables | Closed | high | 2026-06-25 | 2026-06-25 |
| [BG0045](BG0045-audit-bug-readiness-headings-disagree-with-shipped-template.md) | audit bug-readiness check disagrees with the shipped bug template, so every template-authored bug flags "underspecified" | Closed | medium | 2026-07-04 | 2026-07-04 |
| [BG0046](BG0046-duplicate-id-gate-trips-on-the-cr-index-templates-dependencies-table.md) | duplicate-id gate trips on the CR index template's own Dependencies table (per-table reset misses headers without a bare "Status" cell) | Closed | medium | 2026-07-04 | 2026-07-04 |
| [BG0047](BG0047-wsjf-size-signal-ranks-new-file-units-as.md) | WSJF size signal ranks new-file units as trivially small, inverting the sprint order | Closed | medium | 2026-07-04 | 2026-07-04 |
| [BG0048](BG0048-provenance-remake-mass-backfills-artifacts-the-adopt-after.md) | provenance remake mass-backfills artifacts the adopt_after cutoff exempts, and double-stamps a non-tool Created-by | Closed | low | 2026-07-04 | 2026-07-04 |
| [BG0049](BG0049-ts-check-ac-matrix-parser-bleeds-into-later.md) | ts-check AC-matrix parser bleeds into later tables (Revision History rows read as AC rows) | Closed | medium | 2026-07-04 | 2026-07-04 |
