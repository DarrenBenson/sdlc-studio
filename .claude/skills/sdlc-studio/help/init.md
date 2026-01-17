# /sdlc-studio init - Bootstrap Pipeline

Auto-detect project type and bootstrap the full SDLC Studio pipeline.

## Usage

```
/sdlc-studio init                    # Auto-detect and bootstrap
/sdlc-studio init --brownfield       # Force existing project mode
/sdlc-studio init --greenfield       # Force new project mode
/sdlc-studio init --skip-trd         # Skip TRD generation
/sdlc-studio init --skip-tests       # Skip test artifact generation
/sdlc-studio init --dry-run          # Show plan without executing
/sdlc-studio init --force            # Overwrite existing artifacts
```

## Detection Logic

| Source Files | Project Config | Decision |
|--------------|----------------|----------|
| Many (>5) | Yes | Brownfield - auto-proceed |
| Some (1-5) | Yes | Brownfield - confirm first |
| None | Yes | Ambiguous - ask user |
| None | No | Greenfield - auto-proceed |

**Brownfield indicators:** `*.py`, `*.ts`, `*.go`, `*.rs`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `tests/`

## Workflow

### Step 1: Show Plan

Before executing, displays:

```
## SDLC Studio Initialisation Plan

**Mode:** Brownfield (existing codebase detected)
**Language:** Python | **Framework:** FastAPI | **Tests:** Yes

### Pipeline Steps
1. [ ] Generate PRD from codebase
2. [ ] Generate TRD from architecture
3. [ ] Generate personas from roles/permissions
4. [ ] Generate epics from PRD features
5. [ ] Generate stories from epics
6. [ ] Generate test strategy
7. [ ] Generate test specs from existing tests

Proceed? [Y/n]
```

### Step 2: Execute Pipeline

```
[1/7] Generating PRD... done (14 features)
[2/7] Generating TRD... done (12 ADRs)
[3/7] Generating personas... done (4 personas)
[4/7] Generating epics... done (3 epics)
[5/7] Generating stories... done (12 stories)
[6/7] Generating test strategy... done
[7/7] Generating test specs... done

Init complete. Run `/sdlc-studio hint` for next step.
```

## Modes

### Brownfield (Existing Codebase)

Runs the full pipeline using `generate` actions:

1. `prd generate` - Reverse-engineer PRD from codebase
2. `trd generate` - Reverse-engineer TRD from architecture
3. `persona generate` - Infer personas from roles/permissions
4. `epic` - Generate Epics from PRD
5. `story` - Generate Stories from Epics
6. `test-strategy generate` - Infer strategy from codebase
7. `test-spec generate` - Reverse-engineer from existing tests

### Greenfield (New Project)

Creates folder structure and runs guided walkthroughs:

1. Create `sdlc-studio/` directory structure
2. Run `prd create` - Guided PRD conversation
3. Run `trd create` - Guided TRD conversation
4. Run `persona` - Guided persona creation

Remaining artifacts are generated after guided input completes.

## Partial State Handling

If some artifacts already exist:

```
## Existing Artifacts Detected

- PRD: exists (14 features)
- TRD: exists (12 ADRs)
- Personas: exists (4 personas)
- Epics: missing
- Stories: missing

Options:
1. Continue from gap (generate epics, stories, tests)
2. Regenerate all (--force)
3. Cancel

Choice: [1/2/3]
```

## Options

| Option | Description |
|--------|-------------|
| `--force` | Overwrite existing artifacts |
| `--skip-trd` | Skip TRD generation |
| `--skip-tests` | Skip test-strategy and test-spec generation |
| `--greenfield` | Force greenfield mode (new project) |
| `--brownfield` | Force brownfield mode (existing codebase) |
| `--dry-run` | Show plan without executing |

## Examples

```
# Auto-detect and bootstrap
/sdlc-studio init

# Force brownfield mode on a project with few source files
/sdlc-studio init --brownfield

# Bootstrap without test artifacts
/sdlc-studio init --skip-tests

# Preview what would be generated
/sdlc-studio init --dry-run

# Re-initialise, overwriting existing
/sdlc-studio init --force
```

## Output

Creates full `sdlc-studio/` directory structure:

```
sdlc-studio/
  prd.md
  trd.md
  personas.md
  definition-of-done.md
  epics/
    _index.md
    EP0001-*.md
  stories/
    _index.md
    US0001-*.md
  testing/
    strategy.md
    specs/
      _index.md
      TSP0001-*.md
```

## Next Steps

After init completes:

- Run `/sdlc-studio hint` for suggested next action
- Run `/sdlc-studio status` for full pipeline overview
- Run `/sdlc-studio code plan` to start development

## See Also

- `/sdlc-studio hint` - Get single actionable next step
- `/sdlc-studio status` - Check pipeline state
- `/sdlc-studio prd help` - PRD generation details
