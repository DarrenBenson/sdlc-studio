<!--
Load: When you need the full catalogue of reference files or template paths
Dependencies: SKILL.md (always loaded first)
Related: SKILL.md "Progressive Loading Guide" (routing), help/help.md (commands)
-->

# /sdlc-studio - Reference & Template Catalogue

Full index of `reference-*.md` workflow files and the `templates/` structure. SKILL.md
routes to the specific reference file you need via its Progressive Loading Guide; this page
is the complete catalogue for discovery.

## Workflow Reference Files

For detailed step-by-step workflows:

- `reference-prd.md`, `reference-trd.md`, `reference-persona.md` - PRD, TRD, Persona workflows
- `reference-epic.md`, `reference-story.md`, `reference-bug.md` - Epic, Story, Bug workflows
- `reference-project.md` - Project-level orchestration across all epics
- `reference-code.md` - Code plan, implement, verify, check, test workflows
- `reference-refactor.md` - Code refactor, review workflows
- `reference-tsd.md` - TSD, status dashboard workflows
- `reference-test-spec.md` - Test specification workflows
- `reference-test-automation.md` - Test automation, test environment workflows

## Foundational References

**Philosophy:** `reference-philosophy.md` - **Read this first.** Explains Create vs Generate modes and why generate mode produces migration blueprints, not documentation.

**Decisions:** `reference-decisions.md` - Decision impact matrix, TDD decision tree, Ready status criteria, cross-stage validation checkpoints.

**Configuration:** `reference-config.md` - Project configuration options for coverage targets, story quality gates, and thresholds.

**Doctrine:** `reference-doctrine.md` - Project-agnostic operating discipline for onboarding a Claude to any project.

## Help Files

`help/help.md` (main), `help/{type}.md` (type-specific), `help/arguments.md` (full flag reference), `help/upgrade.md` (schema upgrade), `help/reconcile.md` (status reconciliation)

## Full Reference Catalogue

`reference-prd.md`, `reference-trd.md`, `reference-persona.md`, `reference-persona-generate.md`, `reference-consult.md`, `reference-chat.md`, `reference-workflow-personas.md` (Requirements), `reference-epic.md`, `reference-story.md`, `reference-bug.md`, `reference-cr.md` (Specifications), `reference-architecture.md` (Architecture), `reference-code.md` (Code, Test), `reference-refactor.md` (Refactoring, Review), `reference-review.md` (Unified document review), `reference-audit.md` (Adversarial audit harness), `reference-project.md` (Project orchestration), `reference-agentic-lessons.md` (Production lessons for agentic execution), `reference-agent-prompt-template.md` (Agentic wave prompt structure), `reference-operator-heuristics.md` (Cross-cutting operator patterns: memory-drift, incident localisation, release-gate), `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` (Test artifacts), `reference-test-best-practices.md` (Test pitfalls and anti-patterns), `reference-test-validation.md` (Validation workflows), `reference-test-e2e-guidelines.md` (E2E patterns), `reference-upgrade.md` (Schema migration), `reference-reconcile.md` (Status reconciliation), `reference-repo-map.md` (AST repo indexer), `reference-verify.md` (Executable AC verifier DSL), `reference-github-sync.md` (GitHub Issues two-way sync), `reference-scripts.md` (Skill-internal scripts convention), `reference-doctrine.md` (Operating doctrine), `reference-deploy-readiness.md` (Deploy readiness patterns), `reference-rfc.md` (RFC design exploration), `reference-plan-files.md` (Plan-file lifecycle)

## Templates (v2 modular structure)

- Core: `templates/core/*.md` (prd, trd, tsd, epic, story, plan, test-spec, bug, cr)
- Personas: `templates/personas/` (persona-template, archetypes by category)
- Indexes: `templates/indexes/*.md` (epic, story, plan, bug, test-spec, review)
- Modules: `templates/modules/trd/*.md` (c4-diagrams, container-design, adr), `templates/modules/tsd/*.md` (contract-tests, performance-tests, security-tests), `templates/modules/epic/*.md` (engineering-view, product-view, test-view)
- Config: `templates/config-defaults.yaml`, `templates/config.yaml`, `templates/version.yaml`
- Automation: `templates/automation/*.template` (pytest, jest, vitest, go, xunit, junit)
