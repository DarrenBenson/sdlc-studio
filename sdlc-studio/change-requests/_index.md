# Change Request Index

**Last Updated:** 2026-06-20

## Summary

| Status | Count |
| --- | --- |
| Proposed | 10 |
| Approved | 0 |
| In Progress | 0 |
| Complete | 10 |
| Rejected | 0 |
| Deferred | 0 |
| Superseded | 1 |
| Blocked | 0 |
| **Total** | **21** |

## All Changes

| ID | Title | Status | Priority | Type | Date | Linked Epics |
| --- | --- | --- | --- | --- | --- | --- |
| [CR-0001](CR0001-doc-accuracy-fixes.md) | Documentation accuracy - command-vs-script scope and metadata convention | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0002](CR0002-add-deterministic-duplicate-id-collision-detector.md) | Add deterministic duplicate-ID / collision detector; census scripts silently collapse colliding IDs | Complete | High | Improvement | 2026-06-20 | -- |
| [CR-0003](CR0003-add-referential-integrity-check-for-required-epic.md) | Add referential-integrity check for required Epic/Story link fields and dangling ID references | Complete | High | Improvement | 2026-06-20 | EP0005 |
| [CR-0004](CR0004-review-prep-staleness-uses-filesystem-mtime-and-ra.md) | review_prep staleness uses filesystem mtime and raw-string timestamp comparison, breaking determinism across clones and timestamp formats | Complete | High | Improvement | 2026-06-20 | EP0005 |
| [CR-0005](CR0005-verify-ac-py-writes-no-report-in-dry-run-and-overw.md) | verify_ac.py writes no report in dry-run and overwrites a single report with no run history | Proposed | Medium | Improvement | 2026-06-20 | -- |
| [CR-0006](CR0006-add-a-graded-llm-judge-verifier-verb-to-verify-ac.md) | Add a graded/LLM-judge verifier verb to verify_ac DSL for AI-output and qualitative ACs | Proposed | Medium | Improvement | 2026-06-20 | -- |
| [CR-0007](CR0007-add-epic-implement-resume-that-reads-the-workflow.md) | Add epic implement --resume that reads the workflow execution table and restarts at the first non-Done story | Proposed | High | Improvement | 2026-06-20 | -- |
| [CR-0008](CR0008-collapse-three-way-config-defaults-duplication-and.md) | Collapse three-way config-defaults duplication and make one source authoritative that scripts actually read | Proposed | Medium | Improvement | 2026-06-20 | -- |
| [CR-0009](CR0009-make-best-practices-guides-sliceable-and-load-once.md) | Make best-practices guides sliceable and load-once; a TypeScript code plan misses the DOM guidance it delegates to javascript.md | Proposed | Medium | Improvement | 2026-06-20 | -- |
| [CR-0010](CR0010-prd-performance-nfr-cites-non-existent-scripts-tes.md) | PRD Performance NFR cites non-existent 'scripts/tests timings' evidence | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0011](CR0011-prd-plan-file-lifecycle-location-omits-its-backing.md) | PRD Plan-file lifecycle Location omits its backing script scripts/plan.py | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0012](CR0012-trd-adr-001-corpus-counts-contradict-the-component.md) | TRD ADR-001 corpus counts contradict the Component Overview table and reality | Proposed | Low | Improvement | 2026-06-20 | -- |
| [CR-0013](CR0013-trd-deployment-topology-lists-six-targets-but-hide.md) | TRD deployment topology lists six targets but hides that codex and agents share one directory | Proposed | Low | Improvement | 2026-06-20 | -- |
| [CR-0014](CR0014-tsd-and-ep0008-hard-code-181-as-a-gate-ac-criterio.md) | TSD and EP0008 hard-code '181' as a gate/AC criterion, coupling them to a count that changes every release | Proposed | Low | Improvement | 2026-06-20 | -- |
| [CR-0015](CR0015-tsd-claims-a-workspace-write-confinement-test-that.md) | TSD claims a workspace write-confinement test that does not exist | Proposed | Medium | Improvement | 2026-06-20 | -- |
| [CR-0016](CR0016-all-eight-audit-filed-crs-carry-an-identical-place.md) | All eight audit-filed CRs carry an identical placeholder AC that asserts nothing about the change | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0017](CR0017-cr0005-evidence-is-partly-false-it-claims-verify-a.md) | CR0005 evidence is partly false: it claims verify_ac writes the report 'with no timestamp', but write_report emits generated_at | Proposed | Low | Improvement | 2026-06-20 | -- |
| [CR-0018](CR0018-sprint-retro-lessons-folder.md) | Sprint retro and committed lessons-learned folder | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0019](CR0019-progressive-disclosure-archived-indexes.md) | Progressive-disclosure indexes with release archival | Superseded | High | Improvement | 2026-06-20 | -- |
| [CR-0020](CR0020-autosprint-phase2-guardrails-ledger.md) | Autosprint Phase 2 - deterministic guardrails, decisions ledger, autonomous wiring | Complete | High | Feature | 2026-06-20 | EP0007 |
| [CR-0021](CR0021-autosprint-tranche-audit-step.md) | Autosprint tranche-audit step (pre-flight grooming) | Complete | High | Feature | 2026-06-20 | EP0007 |
