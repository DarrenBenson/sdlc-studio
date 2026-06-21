<!--
Load: When constructing a command and you need the full flag reference
Dependencies: SKILL.md (always loaded first)
Related: help/help.md (short "Common Options" list), SKILL.md "Arguments" pointer
-->

# /sdlc-studio - Argument Reference

Full command-line argument reference. For the common subset, see `help/help.md`
"Common Options". For per-type flags, see `help/{type}.md`.

| Argument | Description | Default |
| --- | --- | --- |
| `type` | See Type Reference in SKILL.md | Required |
| `action` | create, generate, review, plan, verify, check, list, fix, close, accept, propose, **help** | varies |
| `--output` | Output path (file or directory) | varies by type |
| `--prd` | PRD file path (for epic) | sdlc-studio/prd.md |
| `--epic` | Specific epic ID | all epics |
| `--perspective` | Epic breakdown focus (engineering, product, test) | balanced |
| `--story` | Specific story ID | auto-select |
| `--bug` | Specific bug ID | auto-select |
| `--cr` | Specific change request ID | auto-select |
| `--severity` | Bug severity filter (critical, high, medium, low) | all |
| `--spec` | Specific test spec ID (for test-automation) | all specs |
| `--type` | Test type filter (unit, integration, api, e2e) | all types |
| `--framework` | Override framework detection | auto-detect |
| `--personas` | Personas directory path | sdlc-studio/personas/ |
| `--from-prd` | Generate personas from PRD (persona generate) | - |
| `--from-code` | Generate personas from codebase (persona generate) | - |
| `--with-personas` | Force persona consultation in workflows | false |
| `--skip-personas` | Skip persona consultation in workflows | false |
| `--workshop` | Multi-persona discussion (chat) | - |
| `--amigos` | Three Amigos participants (chat/consult) | false |
| `--context` | Load artefact for context (chat) | - |
| `--force` | Overwrite existing files | false |
| `--no-fix` | Report without auto-fixing (code check, review) | false |
| `--scope` | Reconcile scope: epics, stories, prd, indexes (reconcile) | all |
| `--verbose` | Detailed test output | false |
| `--env` | Test environment (local, docker) | local |
| `--plan` | Specific plan ID (for implement) | auto-select |
| `--tdd` | Force TDD mode (for implement) | plan recommendation |
| `--no-tdd` | Force Test-After mode (for implement) | plan recommendation |
| `--docs` | Update documentation (for implement) | true |
| `--no-docs` | Skip documentation updates (for implement) | false |
| `--from-phase` | Resume workflow from phase N (for story implement) | 1 |
| `--skip` | Skip specific story (for epic implement) | none |
| `--agentic` | Autonomous epic/project execution with concurrent story waves | false |
| `--no-artifacts` | Suppress plan/test-spec/workflow file creation (agentic mode only) | false |
| `--commit-strategy` | Commit granularity: `per-wave`, `per-epic` (default), `per-project` | per-epic |
| `--from` | Generation starting point for project implement: `stories`, `epics` | none |
| `--yes` | Auto-approve generated artifacts (skip pause after `--from`) | false |
| `--dry-run` | Preview changes without applying (for refactor) | false |
| `--focus` | Review focus area (patterns, security, performance, testing, all) | all |
| `--severity` | Minimum severity to report (for review) | all |
| `--quick` | Use cached status results (for status), skip cascade (for epic review) | varies |
| `--full` | Run fresh status analysis | false |
| `--resume` | Resume cascading review from pause point | false |

## Autosprint, Gate & Product

| Argument | Description | Default |
| --- | --- | --- |
| `--goal` | Autosprint stop condition: `done` (deliver) or `design` (groom a backlog) | done |
| `--order` | Autosprint batch order: `priority` then WSJF, or `manual` | priority |
| `--bugs` | Autosprint batch: bugs by state (e.g. `--bugs open`) | - |
| `--crs` | Autosprint batch: CRs by state (e.g. `--crs proposed`) | - |
| `--only` | Gate: run only these checks (comma-separated) | all |
| `--skip` | Gate: skip these checks (comma-separated) | none |
| `--root` | Repo root for scripts (gate, reconcile, doc_coverage, ...) | . |
| `--format` | Output format where supported: `text` or `json` | text |

Autosprint reuses `--epic` (deliver one epic) and `--agentic` / `--commit-strategy` from the
rows above. The gate's checks are conformance, reconcile, validate, constitution, integrity,
duplicate-id, provenance, doc-coverage (see `reference-autosprint.md` and `scripts/gate.py`).
