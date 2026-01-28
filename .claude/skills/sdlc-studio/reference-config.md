# SDLC Studio Configuration Reference

Project-level configuration for customising SDLC Studio behaviour.

## Configuration Files

| File | Location | Purpose |
|------|----------|---------|
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

```yaml
coverage:
  unit: 90          # Target unit test coverage %
  integration: 85   # Target integration coverage %
  e2e: 100          # Target feature coverage % (100 = all features)
```

| Setting | Default | Used In | Notes |
|---------|---------|---------|-------|
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

```yaml
story_quality:
  edge_cases:
    api: 8          # Minimum edge cases for API stories
    other: 5        # Minimum edge cases for non-API stories
  test_scenarios:
    api: 10         # Minimum test scenarios for API stories
    ui: 8           # Minimum test scenarios for UI stories
  sizing:
    max_ac: 10      # Flag story if AC count exceeds this
    max_points: 13  # Flag story if points exceed this
    recommended_ac:
      min: 3        # Recommended minimum AC per story
      max: 5        # Recommended maximum AC per story
```

### Edge Cases

| Setting | Default | Used In |
|---------|---------|---------|
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
|---------|---------|---------|
| `test_scenarios.api` | 10 | story template |
| `test_scenarios.ui` | 8 | reference-story |

### Story Sizing

| Setting | Default | Meaning |
|---------|---------|---------|
| `max_ac` | 10 | Story too large if > 10 AC |
| `max_points` | 13 | Story too large if > 13 points |
| `recommended_ac.min` | 3 | Suggest more AC if < 3 |
| `recommended_ac.max` | 5 | Optimal upper bound |

---

## TDD Trigger

Control when TDD mode is recommended over Test-After.

```yaml
tdd:
  edge_case_threshold: 5  # Use TDD if edge cases > this
```

| Setting | Default | Used In |
|---------|---------|---------|
| `edge_case_threshold` | 5 | reference-decisions, help/code |

**Rationale**: Stories with many edge cases benefit from TDD because:
- Tests clarify expected behaviour before implementation
- Edge cases are harder to retrofit
- TDD prevents "happy path only" implementations

---

## E2E Limits

Control when to split E2E spec files.

```yaml
e2e:
  max_tests_per_spec: 50  # Split spec if tests exceed this
```

| Setting | Default | Used In |
|---------|---------|---------|
| `max_tests_per_spec` | 50 | reference-test-e2e-guidelines |

**Why 50?** Larger spec files:
- Take longer to run
- Are harder to parallelise
- Make failures harder to isolate

---

## Epic Perspectives

Available perspectives for epic breakdown.

```yaml
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

```yaml
review:
  severity_levels:
    - critical      # Must address before merge
    - important     # Should address
    - suggestion    # Consider addressing
```

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

```yaml
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

```yaml
# sdlc-studio/.version
schema_version: 2
upgraded_from: 1          # null for new projects
upgraded_at: 2026-01-27T10:30:00Z
skill_version: "1.3.0"
created_at: 2026-01-15T09:00:00Z
```

| Field | Purpose |
|-------|---------|
| `schema_version` | Current template schema (1=legacy, 2=modular) |
| `upgraded_from` | Previous version (for migration tracking) |
| `upgraded_at` | When upgrade was performed |
| `skill_version` | SDLC Studio version |
| `created_at` | When project was initialised |

---

## See Also

- `templates/config-defaults.yaml` - Default values
- `help/init.md` - Project initialisation
- `reference-upgrade.md` - Upgrading between versions
