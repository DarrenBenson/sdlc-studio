# SDLC Studio Configuration Reference

<!-- Load when: reading or changing project configuration, thresholds, or quality-gate knobs -->

## Contents

- [Configuration Files](#configuration-files)
- [Configuration Loading](#configuration-loading)
- [Coverage Targets](#coverage-targets)
- [Story Quality Gates](#story-quality-gates)
- [TDD Trigger](#tdd-trigger)
- [E2E Limits](#e2e-limits)
- [Epic Perspectives](#epic-perspectives)
- [Review Configuration](#review-configuration)
- [Persona Staleness](#personas-staleness-days)
- [Contract Tables](#contract-tables)
- [Release Strategy](#release-strategy)
- [Using Config in Templates](#using-config-in-templates)
- [Example Project Config](#example-project-config)
- [Version File](#version-file)
- [Project Implementation](#project-implementation)
- [See Also](#see-also)

Project-level configuration for customising SDLC Studio behaviour.

> `config-defaults.yaml` (in `templates/`) is the single source of truth for default values; the Default columns below mirror it and are guarded against drift by `scripts/tests/test_config.py` (CR0008). Scripts read it via `scripts/config.py`. Project overrides go in `sdlc-studio/.config.yaml`.

## Configuration Files

| File | Location | Purpose |
| --- | --- | --- |
| `config-defaults.yaml` | `templates/` (skill) | Default values (do not modify) |
| `.config.yaml` | `sdlc-studio/` (project) | Project-specific overrides |
| `.version` | `sdlc-studio/` (project) | Version tracking for upgrades |

## Configuration Loading

```text
1. Load templates/config-defaults.yaml (skill defaults)
2. Check for sdlc-studio/.config.yaml (project overrides)
3. Merge: project values override defaults
4. Use merged config for all commands
```

Project config only needs to specify values that differ from defaults.

---

## Coverage Targets

Control test coverage thresholds used in TSD, status dashboard, and test specs.

| Setting | Default | Used In | Notes |
| --- | --- | --- | --- |
| `unit` | 90 | TSD, status, test-spec | Core business logic coverage |
| `integration` | 85 | TSD | API and database interaction coverage |
| `e2e` | 100 | TSD, e2e-guidelines | Feature file coverage target |

### When to Adjust

- **Lower for legacy code**: Brownfield projects may need 70-80% initially
- **Higher for critical systems**: Financial/medical may require 95%+
- **Lower for prototypes**: Experimental code may use 60%

---

## Story Quality Gates

Control minimum requirements for story readiness.

### Edge Cases

| Setting | Default | Used In |
| --- | --- | --- |
| `edge_cases.api` | 8 | story template, reference-story |
| `edge_cases.other` | 5 | reference-story, reference-decisions |

**API stories require more edge cases** because they handle:

- Input validation
- Authentication/authorisation
- Rate limiting
- Concurrent access
- Network failures

### Test Scenarios

| Setting | Default | Used In |
| --- | --- | --- |
| `test_scenarios.api` | 10 | story template |
| `test_scenarios.ui` | 8 | reference-story |

### Story Sizing

| Setting | Default | Meaning |
| --- | --- | --- |
| `max_ac` | 10 | Story too large if > 10 AC |
| `max_points` | 13 | Story too large if > 13 points |
| `recommended_ac.min` | 3 | Suggest more AC if < 3 |
| `recommended_ac.max` | 5 | Optimal upper bound |

---

## TDD Trigger

Control when TDD mode is recommended over Test-After.

| Setting | Default | Used In |
| --- | --- | --- |
| `edge_case_threshold` | 5 | reference-decisions, help/code |

**Rationale**: Stories with many edge cases benefit from TDD because:

- Tests clarify expected behaviour before implementation
- Edge cases are harder to retrofit
- TDD prevents "happy path only" implementations

---

## E2E Limits

Control when to split E2E spec files.

| Setting | Default | Used In |
| --- | --- | --- |
| `max_tests_per_spec` | 50 | reference-test-e2e-guidelines |

**Why 50?** Larger spec files:

- Take longer to run
- Are harder to parallelise
- Make failures harder to isolate

---

## Epic Perspectives

Available perspectives for epic breakdown.

```text
epic:
  perspectives:
    - engineering   # TRD-aligned (components, APIs, data)
    - product       # PRD-aligned (value, metrics, stakeholders)
    - test          # TSD-aligned (coverage, risk, automation)
```

Used by `/sdlc-studio epic --perspective {name}`.

---

## Review Configuration

Severity levels for review findings.

```text
review:
  severity_levels:
    - critical      # Must address before merge
    - important     # Should address
    - suggestion    # Consider addressing
```

---

## Persona Staleness {#personas-staleness-days}

The Persona Review pass of `/sdlc-studio review` uses this window to decide whether a persona is "stale" (no consult / story / CR reference within the window).

| Setting | Default | Notes |
| --- | --- | --- |
| `staleness_days` | 90 | Days without a touch before a persona is flagged stale |

A project where personas are consulted rarely by design (e.g. stable archetypes) can extend this; a project where personas are expected to be high-touch can shorten it. See `reference-review.md` for the cross-doc check that reads this value.

---

## Contract Tables {#contract-tables}

The structured tables in PRD and TRD that **are** the feature contract. The default anchors (`§3 Feature Inventory`, `§6 Data Models`) match the v2 PRD/TRD templates.

```text
contract_tables:
  prd: "§3 Feature Inventory"
  trd: "§6 Data Models"
```

Override per-project if the project's PRD/TRD use different section anchors. Strings are matched literally against the document's section headings. Setting either to `null` disables the cross-check for that document.

The `code implement` workflow uses these anchors for the **ship-time contract sync** check: when a commit touches files that imply a feature surface change (anything matching `contract_table_paths`, derived per language) but does not touch the named anchors, the workflow warns. See `reference-code.md#ship-time-contract-sync`.

---

## Release Strategy {#release-strategy}

Determines which ship-time guidance the workflow emits.

```text
release_strategy: pr-required    # solo-dev | pr-required | staged-rollout
```

| Value | Ship guidance | When appropriate |
| --- | --- | --- |
| `solo-dev` | Direct commit to `main`, or branch + `git merge --ff-only main` + `git push`. **No PR.** | Single-developer projects (operator + AI assistant). The PR ceremony is friction; reviews happen via Three Amigos consult + verify + check. |
| `pr-required` | `gh pr create` + review + merge. **Default.** | Team projects where PR review is the change gate. |
| `staged-rollout` | Tag + deploy + soak window + promote. The "live" verification depth requires a stable soak before a feature can be marked Done. | Production systems with multi-environment deploys. |

`/sdlc-studio code implement` and `/sdlc-studio epic implement` branch their final-step ship guidance on this value. See `reference-code.md#release-strategy-branch` and `reference-decisions.md#release-strategy-decision`.

---

## Using Config in Templates

Templates can reference config values using `{{config.path.to.value}}` syntax:

```markdown
| Level | Target | Rationale |
|-------|--------|-----------|
| Unit | {{config.coverage.unit}}% | Core business logic |
| Integration | {{config.coverage.integration}}% | API interactions |
```

---

## Example Project Config

```text
# sdlc-studio/.config.yaml
# Legacy Python project with relaxed targets

coverage:
  unit: 75
  integration: 70

story_quality:
  edge_cases:
    api: 6
  sizing:
    max_points: 8     # Prefer smaller stories

tdd:
  edge_case_threshold: 3  # TDD for most stories
```

---

## Version File

The `.version` file tracks schema version for upgrades:

```text
# sdlc-studio/.version
schema_version: 2
upgraded_from: 1          # null for new projects
upgraded_at: 2026-01-27T10:30:00Z
skill_version: "1.3.0"
created_at: 2026-01-15T09:00:00Z
```

| Field | Purpose |
| --- | --- |
| `schema_version` | Current template schema (1=legacy, 2=modular) |
| `upgraded_from` | Previous version (for migration tracking) |
| `upgraded_at` | When upgrade was performed |
| `skill_version` | SDLC Studio version |
| `created_at` | When project was initialised |

---

## Project Implementation

Control behaviour of `/sdlc-studio project implement`.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `commit_strategy` | enum | `per-epic` | When to auto-commit: after each wave, each epic, or at project end |
| `review_interval` | int | `3` | Run `review --quick` after this many epics |
| `auto_reconcile` | bool | `true` | Automatically reconcile after each epic completes |
| `auto_commit` | bool | `true` | Automatically commit at strategy boundaries |

---

## See Also

- `templates/config-defaults.yaml` - Default values
- `help/init.md` - Project initialisation
- `reference-upgrade.md` - Upgrading between versions
- `reference-project.md` - Project-level orchestration
