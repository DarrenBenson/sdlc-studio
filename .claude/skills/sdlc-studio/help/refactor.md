<!--
Load: On /sdlc-studio code refactor or /sdlc-studio code refactor help
Dependencies: SKILL.md (always loaded first)
Related: reference-refactor.md (deep workflow), reference-code.md (implementation)
-->

# /sdlc-studio code refactor - Guided Refactoring

> **Source of truth:** `reference-refactor.md` - Detailed workflow steps

## Quick Reference

```bash
/sdlc-studio code refactor                        # Interactive selection
/sdlc-studio code refactor --type extract-method  # Specific refactoring
/sdlc-studio code refactor --story US0001         # Refactor story code
/sdlc-studio code refactor --file src/api.ts      # Refactor specific file
/sdlc-studio code refactor --dry-run              # Preview without applying
```

## Prerequisites

- Tests must pass before refactoring (safety net)
- Code must be under version control
- Story should be in Review or Done status (not in active development)

## Refactoring Types

### extract-method

Extract a block of code into a named method.

**What happens:**

1. Identify code block to extract
2. Determine parameters (variables used from outer scope)
3. Determine return value (variables needed after block)
4. Create new method with meaningful name
5. Replace original block with method call
6. Run tests to verify behaviour preserved

**Example:**

```text
Before: 50-line function with nested validation logic
After: Main function + validateInput() + validatePermissions()
```

### extract-variable

Replace a complex expression with a named variable.

**What happens:**

1. Identify expression to extract
2. Choose descriptive name
3. Declare variable with expression value
4. Replace all occurrences of expression
5. Run tests

### rename

Rename a symbol with scope-aware updates.

**What happens:**

1. Identify symbol (variable, function, class, file)
2. Detect all references in scope
3. Preview changes across files
4. Apply rename to all references
5. Update imports if file rename
6. Run tests

### inline

Replace a variable or trivial method with its value.

**What happens:**

1. Identify single-use variable or trivial method
2. Find all usage sites
3. Replace with actual value/body
4. Remove original declaration
5. Run tests

### move

Move code to a more appropriate location.

**What happens:**

1. Identify code to move (function, class, constant)
2. Determine target location (module, class)
3. Move code
4. Update all imports/references
5. Run tests

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--type` | Refactoring type (extract-method, extract-variable, rename, inline, move) | interactive |
| `--story` | Target story's code | all code |
| `--file` | Target specific file | auto-detect |
| `--dry-run` | Preview without applying | false |

## Safe Refactoring Principles

1. **Tests first** - Ensure tests pass before starting
2. **Small steps** - One refactoring at a time
3. **Verify after each** - Run tests after every change
4. **Commit often** - Save progress frequently

## Output

**Console output:**

- Detected code to refactor
- Preview of changes
- Files modified
- Tests run result
- Summary of refactoring applied

**Example output:**

```markdown
## Refactoring: extract-method

### Target
src/handlers/auth.ts:45-89 (validateUserCredentials block)

### Changes
| File | Lines | Change |
|------|-------|--------|
| src/handlers/auth.ts | 45-89 | Extracted to validateCredentials() |
| src/handlers/auth.ts | 91 | Added call to validateCredentials() |

### Tests
✓ All 24 tests passing

### Summary
- Extracted 44 lines to 1 new method
- Reduced handleLogin() from 120 to 77 lines
- No behaviour changes detected
```

## Examples

```bash
# Interactive refactoring selection
/sdlc-studio code refactor

# Extract method from long function
/sdlc-studio code refactor --type extract-method --file src/handlers/auth.ts

# Rename across codebase
/sdlc-studio code refactor --type rename

# Preview refactoring without applying
/sdlc-studio code refactor --type extract-variable --dry-run

# Refactor code for a specific story
/sdlc-studio code refactor --story US0003
```

## Next Steps

After refactoring:

```bash
/sdlc-studio code test          # Verify tests still pass
/sdlc-studio code check         # Run quality checks
/sdlc-studio code verify        # Verify AC still met
```

## See Also

- `reference-refactor.md` - Detailed refactoring workflows
- `/sdlc-studio code review help` - Code review workflow
- `/sdlc-studio code help` - Full code command reference
