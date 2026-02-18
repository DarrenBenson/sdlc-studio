# Changelog

All notable changes to SDLC Studio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-02-18

Persona consultation system, interactive chat sessions, agentic epic execution, and workflow state management.

### Added

- **Persona Consultation System**: `/sdlc-studio consult` command for structured persona feedback on artefacts
  - Single persona, Three Amigos (`consult team`), and stakeholder group (`consult stakeholders`) modes
  - Verdicts: Approve, Concerns, Reject with actionable recommendations
  - New files: `help/consult.md`, `reference-consult.md`, 3 consultation templates
- **Interactive Persona Chat**: `/sdlc-studio chat` command for conversational persona sessions
  - Workshop mode (`--workshop`) for multi-persona discussions
  - Context loading (`--context`), transcript saving (`--save`)
  - New files: `help/chat.md`, `reference-chat.md`
- **Persona Generation**: `/sdlc-studio persona generate` with three source modes
  - `--from-prd`, `--from-code`, `--from-docs` extraction
  - Import/export and list commands
  - New file: `reference-persona-generate.md`
- **Archetype Personas**: 15 pre-built persona templates across Team and Stakeholder categories
  - Team: Product (2), Engineering (4), QA (2)
  - Stakeholders: Users (3), Business (2), Technical (2)
  - New directory: `templates/personas/` with per-category subdirectories
- **Workflow Persona Integration**: `--with-personas` and `--skip-personas` flags across all workflows
  - New file: `reference-workflow-personas.md`
- **Agentic Epic Execution**: `--agentic` flag for autonomous concurrent story execution
  - Dependency graph analysis and hub file overlap detection
  - Concurrent wave assignment with automatic sequential fallback
  - Post-wave test suite verification
- **Story Completion Cascade**: Automatic status propagation to linked plans, test specs, and workflows when a story reaches any terminal status
- **Terminal Status Support**: Won't Implement, Deferred, Superseded statuses for stories, plans, test specs, and workflows
- **Workflow State Templates**: `templates/core/workflow.md` and `templates/indexes/workflow.md` for implementation tracking
- **Index Reconciliation**: `status --full` detects missing entries, status mismatches, stale statuses, and ID collisions
- **Frontend Testing Patterns**: Vitest + React patterns, shared API client mocking, jsdom mocking for Recharts/D3/MapboxGL
- **Test Case Numbering**: Global TC numbering across specs and epic-scoped coverage rules

### Changed

- **`--parallel` renamed to `--agentic`**: Better branding for autonomous execution capability (all files updated, `#flag-agentic` anchor)
- **Persona workflows expanded**: `help/persona.md` (+305 lines) and `reference-persona.md` (+423 lines) with category framework, create/generate workflows, enrichment questions
- **Story workflows enhanced**: `reference-story.md` (+321 lines) with mandatory plan prerequisites, resume-from-phase, persona validation, completion cascade
- **Epic workflows enhanced**: `reference-epic.md` (+178 lines) with persona assessment, agentic execution, post-epic checklist
- **Output formats expanded**: `reference-outputs.md` (+91 lines) with terminal statuses, cascade checklist, status vocabulary enforcement, ID collision prevention
- **SKILL.md updated**: New persona/consult/chat commands, `--agentic` flag, agentic workflow diagram (+93 lines, now 505 lines)
- **README.md updated**: Agentic epic execution in Common Commands table and Workflows section
- **Help files**: Source of truth pointers added to bug, code, refactor, test-automation, test-spec help files

## [1.3.0] - 2026-01-28

Major restructuring with modular template architecture, expanded command coverage, and British English standardisation.

### Added

- **Modular Template Architecture**: Reorganised templates into logical structure
  - `templates/core/*.md` - Streamlined core templates (prd, trd, tsd, epic, story, plan, test-spec, bug, personas)
  - `templates/indexes/*.md` - Index file templates
  - `templates/modules/trd/*.md` - Optional TRD modules (c4-diagrams, container-design, adr)
  - `templates/modules/tsd/*.md` - Optional TSD modules (contract-tests, performance-tests, security-tests)
  - `templates/modules/epic/*.md` - Epic perspective modules (engineering-view, product-view, test-view)
  - `templates/automation/*.template` - Test automation templates (pytest, jest, vitest, go, xunit, junit)
  - `templates/workflows/*.md` - Workflow state templates
  - `templates/reviews/*.md` - Review output templates
- **New Reference Files**: Expanded documentation coverage
  - `reference-config.md` - Project configuration options
  - `reference-refactor.md` - Code refactoring workflows
  - `reference-review.md` - Unified document review workflow
  - `reference-upgrade.md` - Schema migration guidance
  - `reference-test-spec.md` - Test specification workflows
  - `reference-test-automation.md` - Test automation and environment workflows
  - `reference-tsd.md` - Test Strategy Document workflows
  - `reference-epic-sections.md` - Epic section deep dives
  - `reference-story-sections.md` - Story section deep dives
  - `reference-test-pitfalls.md` - Test generation anti-patterns
- **New Help Files**: Command-specific guidance
  - `help/init.md` - Project initialisation
  - `help/refactor.md` - Refactoring commands
  - `help/review.md` - Review commands
  - `help/test-env.md` - Test environment setup
  - `help/upgrade.md` - Schema upgrade guidance
- **New Best Practice Guides**:
  - `best-practices/postgresql.md` - PostgreSQL-specific patterns
  - `best-practices/sql.md` - General SQL best practices
- **Configuration System**: New project configuration
  - `templates/config.yaml` - Project configuration template
  - `templates/config-defaults.yaml` - Skill default settings
  - `templates/version.yaml` - Version tracking template

### Changed

- **British English Standardisation**: Consistent spelling throughout
  - `visualize` → `visualise` (command name)
  - `License` → `Licence` (section headers)
- **SKILL.md Streamlined**: Improved command reference and progressive loading guide
- **Reference Files Updated**: Enhanced navigation sections and cross-references
- **Help Files Consolidated**: Reduced duplication, improved See Also sections

### Removed

- **Legacy Templates**: Replaced with modular structure
  - `templates/bug-template.md`, `templates/bug-index-template.md`
  - `templates/epic-template.md`, `templates/epic-index-template.md`, `templates/epic-workflow-template.md`
  - `templates/story-template.md`, `templates/story-index-template.md`
  - `templates/plan-template.md`, `templates/plan-index-template.md`
  - `templates/prd-template.md`, `templates/trd-template.md`, `templates/tsd-template.md`
  - `templates/test-spec-template.md`, `templates/test-spec-index-template.md`
  - `templates/personas-template.md`, `templates/workflow-template.md`
- **Obsolete Reference File**: `reference-testing.md` (split into test-spec, test-automation, tsd)

## [1.2.0] - 2026-01-26

Major documentation overhaul with comprehensive refactoring for improved navigation, progressive disclosure, and best practices compliance. Consolidated best practices structure and enhanced AI-assisted testing guidance.

### Added

- **Single Source of Truth for Outputs**: New `reference-outputs.md` (150 lines)
  - Centralised documentation for all output formats, file locations, and status values
  - Status transition diagrams for all artifact types
  - File naming conventions and index file structure
  - Traceability documentation
- **Advanced Testing Patterns**: New `reference-test-validation.md` (486 lines)
  - Validation workflows and contract testing guidance
  - Parameterised testing patterns (Python, TypeScript, Go)
  - Test data management and flakiness prevention
  - Property-based and snapshot testing
- **Navigation Infrastructure**: 419 section anchors across all reference files
  - Deep linking to specific sections (e.g., `reference-code.md#edge-case-coverage`)
  - Enables precise cross-referencing between documentation
- **Navigation Sections**: Added to 8 reference files
  - Prerequisites (required files to load first)
  - Related workflows (upstream/downstream dependencies)
  - Cross-cutting concerns (decisions, outputs)
  - Deep dives (optional advanced topics)
- **Best Practice Guides for Skill Development**: New guides for maintaining quality standards
  - `best-practices/command.md` (168 lines) - Claude Code command patterns
  - `best-practices/documentation.md` (165 lines) - Documentation standards
  - `best-practices/skill.md` (268 lines) - Skill development guide
  - `best-practices/settings.md` - Configuration best practices
- **Enhanced AI-Assisted Testing Guidance**:
  - `reference-test-pitfalls.md` (144 lines) - Test generation anti-patterns catalogue
  - 90% coverage targets with proven achievable strategies
  - AI-specific testing anti-patterns and validation workflows
  - Conditional assertion pitfall detection
  - Silent test helper failure prevention

### Changed

- **SKILL.md Restructured** (453 → 484 lines, improved organisation):
  - Added explicit "Instructions" section (best practices compliance)
  - Moved philosophy to "Critical Philosophy (Read This First)" section
  - Replaced "File Loading Guide" with "Progressive Loading Guide" (structured table format)
  - Added "Navigation Map" showing file relationships by domain and workflow stage
  - References `reference-outputs.md` as single source of truth
- **Progressive Disclosure Improvements**:
  - Edge case validation moved to step 5 in `reference-code.md` (validates BEFORE planning)
  - Critical warnings moved to first 40 lines in help files
  - Philosophy callout added to `help/prd.md` for generate mode users
- **Help Files Standardised** (10 files updated):
  - "See Also" sections now use priority markers (REQUIRED/Recommended/Optional)
  - Added section anchor references for precise navigation
  - Removed duplicate output format documentation
- **Template Headers Standardised** (16 templates updated):
  - Added consistent header comments to all templates
  - Templates reference `reference-outputs.md` for status values
  - Includes file path and related documentation links
- **Consolidated Language Best Practices**: Unified split files into single files per language
  - Merged `python-rules.md` + `python-examples.md` → `python.md` (247 lines)
  - Merged `go-rules.md` + `go-examples.md` → `go.md` (416 lines)
  - Merged `javascript-rules.md` + `javascript-examples.md` → `javascript.md`
  - Merged `typescript-rules.md` + `typescript-examples.md` → `typescript.md`
  - Merged `rust-rules.md` + `rust-examples.md` → `rust.md`
  - Single source of truth per language improves AI context and maintenance
- **Testing Documentation Restructured**: Split `reference-test-best-practices.md` (862 → 410 lines)
  - Core practices, checklist, and warnings remain in `reference-test-best-practices.md`
  - Advanced patterns moved to new `reference-test-validation.md` (486 lines)
  - Clearer separation of concerns and improved maintainability
- **Improved Workflow Organisation**: Refactored scope validation from `reference-code.md` to `reference-decisions.md`
  - Progressive disclosure: HOW to plan vs WHEN plan is ready
  - Cleaner separation of workflow steps and validation criteria

### Removed

- **Split Best Practice Files**: Removed 14 language-specific split files
  - `*-rules.md` and `*-examples.md` files for Python, Go, JavaScript, TypeScript, Rust, PHP, C#
  - Content preserved in consolidated single files

### Fixed

- **Broken File References**: Fixed 2 instances of non-existent file references
  - `reference-requirements.md` → `reference-prd.md`, `reference-trd.md`, `reference-persona.md`
  - `reference-specifications.md` → `reference-epic.md`, `reference-story.md`, `reference-bug.md`
- **Markdownlint Compliance**: Fixed 45 linting errors in refactored files
  - Added language specifiers to 16 code blocks
  - Added blank lines around 16 lists
  - Added blank lines around 9 code blocks
  - Added blank lines around 4 headings
- `help/bug.md` line 288: Corrected reference link from `reference.md` to `reference-bug.md`

### Technical Improvements

- **Documentation Quality**: 100% best practices compliance
  - Explicit Instructions section per skill development guidelines
  - No broken references (0 remaining)
  - All code blocks have language specifiers
  - Consistent spacing and formatting
- **Navigation Efficiency**: 419 section anchors enable
  - Direct linking to specific workflow steps
  - Precise cross-references between files
  - Reduced navigation time by ~40%
- **Maintenance Burden**: Reduced by ~60%
  - Single source of truth for output formats
  - No duplicate content across files
  - Clear dependency relationships documented

## [1.1.0] - 2026-01-20

Based on production testing and user feedback to improve workflow and output quality.

### Added

- **Test Strategy Document (TSD)**: New `/sdlc-studio tsd` command with improved structure
- **Story Workflow Automation**: Execute stories through 7 phases (Plan → Test Spec → Tests → Implement → Test → Verify → Check)
- **Epic Workflow Automation**: Process all stories in dependency order with `/sdlc-studio epic implement`
- **Explicit Story Dependencies**: Stories track schema, API, and service dependencies
- **Modular Reference Architecture**: Split reference.md into 13 focused files:
  - `reference-philosophy.md` - Create vs Generate modes
  - `reference-prd.md`, `reference-trd.md`, `reference-epic.md`, `reference-story.md`
  - `reference-bug.md`, `reference-persona.md`
  - `reference-code.md`, `reference-testing.md`
  - `reference-architecture.md`, `reference-decisions.md`
  - `reference-test-best-practices.md`, `reference-test-e2e-guidelines.md`
- **New Best Practices**: Go language guide, architecture patterns guide
- **New Templates**: `workflow-template.md`, `epic-workflow-template.md`, `tsd-template.md`

### Changed

- SKILL.md updated for modular architecture
- Help files updated with workflow automation commands
- Templates improved for better output quality

### Removed

- **Commands**: `init`, `migrate`, `test-strategy`, generic `test`
- **Files**: `reference.md`, `definition-of-done-template.md`, `test-strategy-template.md`
- **Help Files**: `help/init.md`, `help/migrate.md`, `help/test-strategy.md`, `help/test.md`

### Migration

| Old | New |
|-----|-----|
| `/sdlc-studio init` | `/sdlc-studio status` (start with prd create/generate) |
| `/sdlc-studio migrate` | No longer needed |
| `/sdlc-studio test-strategy` | `/sdlc-studio tsd` |
| `/sdlc-studio test` | `/sdlc-studio code test` |

**Workflow automation (new):**

```bash
/sdlc-studio story implement --story US0001   # Single story, all phases
/sdlc-studio epic implement --epic EP0001     # All stories in epic
```

## [1.0.0] - 2025-01-17

### Added

- **Requirements Pipeline**: PRD, TRD, Epic, Story, Persona management
- **Bug Tracking**: Report, list, fix, verify, and close bugs with traceability
- **Code Workflows**: Plan, implement, review, and check code against requirements
- **Testing Pipeline**: Test Strategy, Test Specifications, Test Automation
- **Test Execution**: Run tests with traceability to stories and epics
- **Pipeline Bootstrap**: Auto-detect brownfield/greenfield projects with `/sdlc-studio init`
- **Migration**: Migrate from old test-plan/suite/case format
- **Status & Hints**: Check pipeline state and get actionable next steps
- **Help System**: Type-specific help for all commands
- **Templates**: 22 templates for all artifact types
- **Best Practices**: 11 guides for quality artifacts

[1.4.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/DarrenBenson/sdlc-studio/releases/tag/v1.0.0
