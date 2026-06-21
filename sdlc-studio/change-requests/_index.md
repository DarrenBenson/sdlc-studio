# Change Request Index

**Last Updated:** 2026-06-20

## Summary

| Status | Count |
| --- | --- |
| Proposed | 3 |
| Approved | 0 |
| In Progress | 0 |
| Complete | 48 |
| Rejected | 0 |
| Deferred | 0 |
| Superseded | 1 |
| Blocked | 0 |
| **Total** | **52** |

## All Changes

| ID | Title | Status | Priority | Type | Date | Linked Epics |
| --- | --- | --- | --- | --- | --- | --- |
| [CR-0001](CR0001-doc-accuracy-fixes.md) | Documentation accuracy - command-vs-script scope and metadata convention | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0002](CR0002-add-deterministic-duplicate-id-collision-detector.md) | Add deterministic duplicate-ID / collision detector; census scripts silently collapse colliding IDs | Complete | High | Improvement | 2026-06-20 | -- |
| [CR-0003](CR0003-add-referential-integrity-check-for-required-epic.md) | Add referential-integrity check for required Epic/Story link fields and dangling ID references | Complete | High | Improvement | 2026-06-20 | EP0005 |
| [CR-0004](CR0004-review-prep-staleness-uses-filesystem-mtime-and-ra.md) | review_prep staleness uses filesystem mtime and raw-string timestamp comparison, breaking determinism across clones and timestamp formats | Complete | High | Improvement | 2026-06-20 | EP0005 |
| [CR-0005](CR0005-verify-ac-py-writes-no-report-in-dry-run-and-overw.md) | verify_ac.py writes no report in dry-run and overwrites a single report with no run history | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0006](CR0006-add-a-graded-llm-judge-verifier-verb-to-verify-ac.md) | Add a graded/LLM-judge verifier verb to verify_ac DSL for AI-output and qualitative ACs | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0007](CR0007-add-epic-implement-resume-that-reads-the-workflow.md) | Add epic implement --resume that reads the workflow execution table and restarts at the first non-Done story | Complete | High | Improvement | 2026-06-20 | EP0007 |
| [CR-0008](CR0008-collapse-three-way-config-defaults-duplication-and.md) | Collapse three-way config-defaults duplication and make one source authoritative that scripts actually read | Complete | Medium | Improvement | 2026-06-20 | EP0008 |
| [CR-0009](CR0009-make-best-practices-guides-sliceable-and-load-once.md) | Make best-practices guides sliceable and load-once; a TypeScript code plan misses the DOM guidance it delegates to javascript.md | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0010](CR0010-prd-performance-nfr-cites-non-existent-scripts-tes.md) | PRD Performance NFR cites non-existent 'scripts/tests timings' evidence | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0011](CR0011-prd-plan-file-lifecycle-location-omits-its-backing.md) | PRD Plan-file lifecycle Location omits its backing script scripts/plan.py | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0012](CR0012-trd-adr-001-corpus-counts-contradict-the-component.md) | TRD ADR-001 corpus counts contradict the Component Overview table and reality | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0013](CR0013-trd-deployment-topology-lists-six-targets-but-hide.md) | TRD deployment topology lists six targets but hides that codex and agents share one directory | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0014](CR0014-tsd-and-ep0008-hard-code-181-as-a-gate-ac-criterio.md) | TSD and EP0008 hard-code '181' as a gate/AC criterion, coupling them to a count that changes every release | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0015](CR0015-tsd-claims-a-workspace-write-confinement-test-that.md) | TSD claims a workspace write-confinement test that does not exist | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0016](CR0016-all-eight-audit-filed-crs-carry-an-identical-place.md) | All eight audit-filed CRs carry an identical placeholder AC that asserts nothing about the change | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0017](CR0017-cr0005-evidence-is-partly-false-it-claims-verify-a.md) | CR0005 evidence is partly false: it claims verify_ac writes the report 'with no timestamp', but write_report emits generated_at | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0018](CR0018-sprint-retro-lessons-folder.md) | Sprint retro and committed lessons-learned folder | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0019](CR0019-progressive-disclosure-archived-indexes.md) | Progressive-disclosure indexes with release archival | Superseded | High | Improvement | 2026-06-20 | -- |
| [CR-0020](CR0020-autosprint-phase2-guardrails-ledger.md) | Autosprint Phase 2 - deterministic guardrails, decisions ledger, autonomous wiring | Complete | High | Feature | 2026-06-20 | EP0007 |
| [CR-0021](CR0021-autosprint-tranche-audit-step.md) | Autosprint tranche-audit step (pre-flight grooming) | Complete | High | Feature | 2026-06-20 | EP0007 |
| [CR-0022](CR0022-autosprint-deps-first-ordering.md) | Dependency-first ordering in autosprint plan | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0023](CR0023-complete-conformance-gate.md) | Complete the conformance gate - reconciled, reviewed, and a recorded critic verdict | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0024](CR0024-rfc-decide-decision-session.md) | `rfc decide` - the multi-RFC decision session | Complete | High | Feature | 2026-06-20 | EP0006 |
| [CR-0025](CR0025-checks-emit-remediation-guidance.md) | deterministic checks emit remediation guidance, not just findings | Complete | High | Feature | 2026-06-20 | EP0005 |
| [CR-0026](CR0026-reconcile-apply-subcommand.md) | reconcile `apply` - mechanical index fixes behind --dry-run | Complete | High | Feature | 2026-06-20 | EP0005 |
| [CR-0027](CR0027-per-project-status-vocab-and-conformance-cutoff.md) | per-project status vocab + conformance adoption cutoff | Complete | High | Feature | 2026-06-20 | EP0005/EP0008 |
| [CR-0028](CR0028-complexity-computation.md) | complexity computation (RFC0009 WS1) | Complete | High | Feature | 2026-06-20 | EP0008 |
| [CR-0029](CR0029-code-plan-complexity-estimation.md) | code plan complexity estimation + refactor-first (RFC0009 WS2) | Complete | High | Feature | 2026-06-20 | EP0008 |
| [CR-0030](CR0030-decompose-apply-type.md) | decompose apply_type (refactor-first on RFC0009's own signal) | Complete | Medium | Improvement | 2026-06-20 | EP0005 |
| [CR-0031](CR0031-validate-no-ac-adoption-cutoff.md) | validate no-ac honours the conformance adoption cutoff | Complete | Medium | Improvement | 2026-06-20 | EP0005 |
| [CR-0032](CR0032-repo-map-honest-lexical-ranker.md) | redocument repo_map as a lexical relevance ranker (RFC0004) | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0033](CR0033-consolidate-test-reference-clique.md) | consolidate the test-reference clique (RFC0008) | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0034](CR0034-personas-generate-on-demand.md) | personas generate on demand from seeds (RFC0007) | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0035](CR0035-deterministic-finding-filer.md) | deterministic Bug/CR/RFC finding filer (RFC0002 WS3) | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0036](CR0036-reference-audit-methodology.md) | reference-audit.md methodology + project lens packs (RFC0002 WS1) | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0037](CR0037-audit-harness-templates.md) | portable audit prompt-harness templates (RFC0002 WS2) | Complete | Medium | Feature | 2026-06-20 | -- |
| [CR-0038](CR0038-autosprint-wsjf-complexity.md) | autosprint --order wsjf + complexity-weighted budget (RFC0009 WS3) | Complete | Medium | Feature | 2026-06-20 | -- |
| [CR-0039](CR0039-audit-skill-profile-pack.md) | package the skill-profile lens pack (RFC0002 WS5) | Complete | Low | Feature | 2026-06-20 | -- |
| [CR-0040](CR0040-project-constitution-gate.md) | optional project constitution + machine-checkable principle gate (RFC0005) | Complete | Medium | Feature | 2026-06-20 | -- |
| [CR-0041](CR0041-progressive-disclosure-indexes.md) | progressive-disclosure indexes with release archival (RFC0012) | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0042](CR0042-transition-helper.md) | deterministic status-transition helper | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0043](CR0043-complexity-churn-test-risk.md) | churn-weighted composite + complexity-driven test risk (RFC0009 WS4) | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0044](CR0044-skill-version-check-self-update.md) | skill version check + consent `skill-update` | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0045](CR0045-deterministic-artifact-write-cascade.md) | deterministic artifact create + cross-link cascade | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0046](CR0046-portable-ci-quality-gate.md) | portable quality-gate entrypoint for CI (ecosystem-neutral) | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0047](CR0047-pvd-template-and-manifest.md) | PVD template + product manifest (RFC0015 WS1) | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0048](CR0048-read-only-pvd-projection-drift-check.md) | read-only PVD projection + drift check (RFC0015 WS2) | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0049](CR0049-product-reconcile-feature-map-traceability.md) | product reconcile - cross-repo feature-map traceability (RFC0015 WS3) | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0050](CR0050-telemetry-record-and-schema.md) | telemetry record + .local/telemetry.jsonl schema (RFC0014 WS1) | Proposed | Medium | Feature | 2026-06-21 | -- |
| [CR-0051](CR0051-telemetry-loop-capture.md) | loop writes a telemetry record per unit close (RFC0014 WS2) | Proposed | Medium | Feature | 2026-06-21 | -- |
| [CR-0052](CR0052-asset-provenance-stamp-misuse-check-remake.md) | asset provenance stamp + misuse check + remake migration | Proposed | Medium | Feature | 2026-06-21 | -- |
