# SDLC Studio Module System

Optional composable sections that extend core templates. Modules provide progressive disclosure - load only what you need.

## Module Loading

Modules are loaded via command flags or when their content is specifically needed:

| Module Path | Loaded By | Purpose |
|-------------|-----------|---------|
| `trd/c4-diagrams.md` | `trd create --with-diagrams` | C4 Context/Container/Component diagrams |
| `trd/container-design.md` | `trd create --with-containers` | Docker/k8s deployment design |
| `trd/adr.md` | `trd create` (always) | ADR template for architectural decisions |
| `tsd/contract-tests.md` | `tsd create`, `test-spec` | Contract test patterns |
| `tsd/performance-tests.md` | `tsd create --with-perf` | Performance/load test patterns |
| `tsd/security-tests.md` | `tsd create --with-security` | Security test patterns |
| `epic/engineering-view.md` | `epic --perspective engineering` | TRD-aligned epic breakdown |
| `epic/product-view.md` | `epic --perspective product` | PRD-aligned epic breakdown |
| `epic/test-view.md` | `epic --perspective test` | TSD-aligned epic breakdown |

## Module Structure

Each module follows a consistent format:

```markdown
<!--
Module: {module-name}
Extends: templates/core/{parent}.md
Section: {section-number} (where to insert in parent)
-->

## {Section Title}

{Module content with {{placeholders}}}
```

## Using Modules

### Automatic Loading

Some modules load automatically based on context:

- **ADR module**: Always included when TRD has architecture decisions
- **Contract tests**: Loaded when E2E tests mock API responses

### Flag-Based Loading

Explicitly request modules with command flags:

```bash
# Load all TRD modules
/sdlc-studio trd create --full

# Load specific modules
/sdlc-studio trd create --with-diagrams --with-containers

# Epic perspectives
/sdlc-studio epic --perspective engineering
/sdlc-studio epic --perspective product
/sdlc-studio epic --perspective test
```

### Combined Flags

The `--full` flag loads all relevant modules for a template type:

| Command | Modules Loaded |
|---------|---------------|
| `trd create --full` | c4-diagrams, container-design, adr |
| `tsd create --full` | contract-tests, performance-tests, security-tests |

## Creating New Modules

1. Identify content that is:
   - Optional for most projects
   - Self-contained (doesn't require other sections)
   - Substantial enough to warrant separation (~30+ lines)

2. Create module file in appropriate subdirectory

3. Update this README with loading information

4. Update the parent template with a placeholder or reference

## Module vs Core Content

**Keep in core template if:**
- Required for all projects
- Less than 30 lines
- Tightly coupled to other sections

**Extract to module if:**
- Optional for many projects
- Self-contained
- Adds significant complexity

## See Also

- `templates/core/` - Streamlined core templates
- `reference-outputs.md` - Output formats and validation
- `SKILL.md` - Command reference with module flags
