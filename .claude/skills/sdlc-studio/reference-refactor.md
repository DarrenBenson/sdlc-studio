# Reference: Refactoring & Code Review Workflows

## Overview

This reference covers the iterative improvement loop between `implement` and `verify` - the refactoring and review commands that ensure code quality before completion.

## Pre-Flight Checks

Before any refactoring operation:

1. **Tests must pass**

   ```bash
   /sdlc-studio code test
   ```

   If tests fail, fix them first. Tests are your safety net.

2. **Code must be committed**

   ```bash
   git status  # Should show clean or committed state
   ```

   Uncommitted changes make rollback difficult.

3. **Story status check**
   - Refactoring during active implementation (In Progress) is risky
   - Prefer refactoring after Review or Done status

## Extract Method Workflow

### When to Use

- Method exceeds 20-30 lines
- Duplicated code blocks across methods
- Nested logic (3+ levels of indentation)
- Code block has a clear, nameable purpose

### Workflow Steps

1. **Identify extraction candidate**
   - Look for logical blocks (validation, transformation, I/O)
   - Check for clear start/end boundaries
   - Note any comments describing the block

2. **Analyse dependencies**

   ```text
   Variables read from outer scope → parameters
   Variables written and used after → return values
   Variables local to block → keep inside
   ```

3. **Determine signature**

   | Analysis | Result |
   |----------|--------|
   | Reads `userId`, `config` | `function extract(userId: string, config: Config)` |
   | Writes `result` used later | `return result` |
   | Multiple writes needed | Return object or use out parameters |

4. **Name the method**
   - Use verb+noun: `validateCredentials`, `parseResponse`, `buildQuery`
   - Name should describe what, not how
   - If naming is hard, the block might not be cohesive

5. **Extract and replace**

   ```typescript
   // Before
   function handleRequest(req: Request) {
     // ... 20 lines of validation ...
     // ... 30 lines of processing ...
   }

   // After
   function handleRequest(req: Request) {
     const validInput = validateInput(req);
     return processRequest(validInput);
   }

   function validateInput(req: Request): ValidatedInput { ... }
   function processRequest(input: ValidatedInput): Response { ... }
   ```

6. **Run tests**
   - All existing tests must pass
   - No behaviour change expected

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Too many parameters | >4 parameters | Group into object |
| Non-cohesive extraction | Hard to name | Extract smaller piece |
| Breaking encapsulation | Exposing private state | Keep method private |

## Extract Variable Workflow

### When to Use

- Complex expressions (especially boolean)
- Magic values without context
- Repeated subexpressions
- Long method chains

### Workflow Steps

1. **Identify expression**

   ```typescript
   // Before: What does this mean?
   if (user.age >= 18 && user.verified && !user.suspended) { ... }
   ```

2. **Choose descriptive name**

   ```typescript
   // After: Clear intent
   const isEligibleUser = user.age >= 18 && user.verified && !user.suspended;
   if (isEligibleUser) { ... }
   ```

3. **Replace all occurrences**
   - If expression appears multiple times, replace all
   - Verify no side effects in expression

4. **Run tests**

### Naming Conventions

| Expression Type | Naming Pattern | Example |
|-----------------|----------------|---------|
| Boolean | `is/has/can/should` prefix | `isValidEmail` |
| Count | `count/num/total` prefix | `totalItems` |
| Limit | `max/min` prefix | `maxRetries` |
| Duration | Unit suffix | `timeoutMs` |

## Rename Workflow

### When to Use

- Name no longer reflects purpose
- Inconsistent naming across codebase
- Abbreviations causing confusion
- Terminology change

### Workflow Steps

1. **Find all references**
   - Use grep/IDE to find all occurrences
   - Include: code, tests, comments, documentation
   - Exclude: unrelated matches (common words)

2. **Classify references**

   | Location | Update Strategy |
   |----------|-----------------|
   | Same file | Direct rename |
   | Same package | Update imports if needed |
   | External API | Consider deprecation |
   | Tests | Update test names too |
   | Docs | Update separately |

3. **Apply rename**
   - Start from declaration
   - Update references in dependency order
   - Update file name if class/module rename

4. **Run tests**
   - Tests should still pass
   - Test names might need updating

### File/Module Rename

When renaming files:

1. Update all import statements
2. Update any configuration referencing the path
3. Update test file names if following naming convention
4. Git will track as rename if >50% similar

## Inline Workflow

### When to Use

- Variable used exactly once
- Trivial method that obscures logic
- Over-abstraction ("enterprise abstractions")
- Indirection without value

### Workflow Steps

1. **Verify single use**

   ```typescript
   // Good candidate: used once
   const email = user.email;
   sendEmail(email);  // →  sendEmail(user.email);

   // Bad candidate: used multiple times
   const email = user.email;
   validate(email);
   sendEmail(email);
   logEmail(email);
   ```

2. **Check for side effects**
   - Pure expression: safe to inline
   - Side effects: inline only at single usage point

3. **Replace and remove**
   - Replace usage with value
   - Delete original declaration

4. **Run tests**

### When NOT to Inline

- Value has semantic meaning (extract variable did this for a reason)
- Value is used in multiple places
- Expression has side effects
- Improves debuggability

## Move Workflow

### When to Use

- Code in wrong module (cohesion)
- Circular dependencies forming
- Feature envy (method uses another class more than its own)
- Utility functions in wrong location

### Workflow Steps

1. **Identify target location**

   | Smell | Target |
   |-------|--------|
   | Feature envy | Move to class being envied |
   | Utility function | Move to shared utils |
   | Domain logic in handler | Move to domain service |
   | Shared code | Move to common module |

2. **Check dependencies**
   - Will move create circular dependency?
   - Will consumers need to update imports?

3. **Move code**
   - Copy to new location first
   - Update references to use new location
   - Delete from old location

4. **Update imports**
   - All files importing from old location
   - Consider re-export for backwards compatibility (temporary)

5. **Run tests**

## Code Review Workflow

### Review Preparation

1. **Gather context**
   - Load story acceptance criteria
   - Load implementation plan
   - Identify files touched

2. **Load best practices**
   - `best-practices/{language}.md`
   - `reference-test-best-practices.md` if reviewing tests

### Review Process

1. **High-level scan**
   - Does structure match plan?
   - Are all AC addressed?
   - Any obvious anti-patterns?

2. **Security review**

   | Check | Look For |
   |-------|----------|
   | Injection | String interpolation in queries |
   | Auth | Missing permission checks |
   | Data | Sensitive data exposure |
   | Input | Unvalidated user input |

3. **Pattern review**

   | Principle | Violation Signs |
   |-----------|-----------------|
   | Single Responsibility | Class/function doing multiple things |
   | Open/Closed | Modifying existing code for extension |
   | Liskov Substitution | Subclass breaking parent contract |
   | Interface Segregation | Implementing unused interface methods |
   | Dependency Inversion | High-level depending on low-level |

4. **Performance review**

   | Issue | Pattern |
   |-------|---------|
   | N+1 queries | Loop with DB call inside |
   | Memory leak | Event listeners not removed |
   | Blocking | Sync I/O in async context |
   | Redundant work | Recomputing same value |

5. **Testability review**
   - Are dependencies injectable?
   - Are side effects isolated?
   - Can units be tested in isolation?

### Report Generation

```markdown
## Code Review: {story_id} - {title}

### Files Reviewed
| File | Lines | Focus |
|------|-------|-------|
| src/auth/login.ts | 45-120 | New implementation |
| src/auth/session.ts | 12-34 | Modified |

### Summary
| Category | Count |
|----------|-------|
| Critical | {n} |
| Important | {n} |
| Suggestions | {n} |

### Critical Issues
{Each with file:line, description, fix suggestion}

### Important Issues
{Each with file:line, description, fix suggestion}

### Suggestions
{Each with file:line, description, optional fix}

### Positive Observations
{Things done well - reinforce good patterns}
```

## Post-Refactoring Verification

After any refactoring:

1. **Run tests**

   ```bash
   /sdlc-studio code test
   ```

2. **Run linters**

   ```bash
   /sdlc-studio code check
   ```

3. **Verify AC** (if story context)

   ```bash
   /sdlc-studio code verify --story {id}
   ```

4. **Commit with clear message**

   ```text
   refactor: extract validateCredentials from handleLogin

   - Reduced handleLogin from 120 to 77 lines
   - No behaviour change
   - All tests passing
   ```

## See Also

- `help/refactor.md` - Command quick reference
- `help/review.md` - Review command reference
- `best-practices/` - Language-specific guidelines
- `reference-code.md` - Implementation workflow
