<!--
Load: On /sdlc-studio review or /sdlc-studio code review or /sdlc-studio epic review or review help
Dependencies: SKILL.md (always loaded first)
Related: reference-review.md (document review), reference-refactor.md (code review), reference-epic.md (epic review cascade)
-->

# Review Commands

SDLC Studio supports three types of reviews:
- **Document review:** Unified PRD, TRD, TSD review with cross-document consistency
- **Epic review:** Cascading review of epic and changed stories (default behaviour)
- **Code review:** Design pattern and quality review of implementation

---

# /sdlc-studio review - Document Review

Review all specification documents together and check cross-document consistency.

## Quick Reference

```bash
/sdlc-studio review                    # Run all document reviews
/sdlc-studio review --quick            # Fast check using cached data
/sdlc-studio review --focus prd        # Run only PRD review
/sdlc-studio review --focus trd        # Run only TRD review
/sdlc-studio review --focus tsd        # Run only TSD review
```

## Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--quick` | Use cached data, skip codebase analysis | false |
| `--focus` | Review specific document only | all |

## What Happens

1. **PRD Review** - Compare features against implementation
2. **TRD Review** - Check architecture matches reality
3. **TSD Review** - Verify coverage and quality gates
4. **Cross-Document Check** - Validate consistency between documents

## Cross-Document Checks

| Check | What It Verifies |
|-------|------------------|
| PRD → TRD | Every feature has architecture documentation |
| TRD → TSD | Every component has test strategy |
| PRD → TSD | Every NFR has a quality gate |

## Example Output

```text
══════════════════════════════════════════════════════════
                   DOCUMENT REVIEW SUMMARY
══════════════════════════════════════════════════════════

📋 PRD REVIEW                          ▓▓▓▓▓▓▓▓░░ 85%
   Features: 14 defined
   ⚠️ 2 features need attention

📐 TRD REVIEW                          ▓▓▓▓▓▓▓▓▓░ 92%
   ✅ Architecture current

🧪 TSD REVIEW                          ▓▓▓▓▓▓▓░░░ 78%
   ⚠️ Coverage below target

──────────────────────────────────────────────────────────
🔗 CROSS-DOCUMENT CONSISTENCY

   PRD → TRD: ✅ 14/14 features have architecture
   TRD → TSD: ⚠️ API tests but no contract tests
   PRD → TSD: ⚠️ NFR "p95 < 200ms" not in quality gates

▶️ NEXT: /sdlc-studio test-automation generate
══════════════════════════════════════════════════════════
```

## See Also

- `reference-review.md` - Detailed review workflows
- `/sdlc-studio status` - Quick dashboard

---

# /sdlc-studio epic review - Cascading Review

Epic review now **cascades by default** - it reviews the epic and all changed stories/code.

## Quick Reference

```bash
/sdlc-studio epic review                  # Cascade review (default)
/sdlc-studio epic review --quick          # Epic only, skip stories
/sdlc-studio epic review --resume         # Resume from pause point
/sdlc-studio epic review --epic EP0001    # Target specific epic
```

## Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--quick` | Skip cascade, review only the epic | false |
| `--resume` | Resume from where review paused | false |
| `--epic` | Target specific epic | next epic |

## What Happens (Cascade Mode)

1. **Build review queue** - Identifies stories/code changed since last review
2. **Review changed stories** - Checks spec against implementation
3. **Review changed code** - Runs code quality checks
4. **Review epic** - Checks epic-level AC and status
5. **Store findings** - Creates RV{NNNN} review files
6. **Update state** - Updates `.local/review-state.json` timestamps

## Modified-Since Detection

Only artifacts changed since their last review are included in cascade:

| Artifact Type | Detection Method |
|---------------|------------------|
| Epic spec | File mtime or git log |
| Story spec | File mtime or git log |
| Story code | Code file mtime or git log |

## Review Findings

Findings are stored in `sdlc-studio/reviews/RV{NNNN}-{artifact-id}-review.md` with severity levels:

| Severity | Meaning | Action |
|----------|---------|--------|
| Critical | Blocks progress | Must address |
| Important | Quality concern | Should address |
| Suggestion | Improvement opportunity | Consider |

## Example Output

```text
## Epic Review: EP0001 - User Authentication

### Cascade Summary
| Type | Reviewed | Skipped | Findings |
|------|----------|---------|----------|
| Story specs | 3 | 2 (unchanged) | 5 |
| Story code | 2 | 3 (unchanged) | 3 |
| Epic | 1 | 0 | 2 |

### Stories Reviewed
- US0001: 2 important issues
- US0003: 1 important issue, 2 suggestions

### Stories Skipped (unchanged since last review)
- US0002: Reviewed 2026-01-25
- US0004: Reviewed 2026-01-26
```

## Resume Capability

If review is interrupted:

```bash
# Review paused mid-execution
# Resume from where it stopped
/sdlc-studio epic review --resume
```

State is persisted in `.local/review-queue.json`.

## Quick Mode

Skip the cascade for a fast status check:

```bash
/sdlc-studio epic review --quick
```

Reviews only epic-level status, no story deep-dive.

---

# /sdlc-studio code review - Design Pattern & Quality Review

## Quick Reference

```bash
/sdlc-studio code review                  # Review next In Progress story
/sdlc-studio code review --story US0001   # Review specific story
/sdlc-studio code review --file src/api.ts  # Review specific file
/sdlc-studio code review --focus security   # Focus on security patterns
```

## Prerequisites

- Story must have implementation (In Progress, Review, or Done status)
- For story-scoped review: Plan must exist with file mappings

## What Happens

1. Load story acceptance criteria and technical notes
2. Explore implementation code
3. Load language best practices (`best-practices/{language}.md`)
4. Identify pattern violations, anti-patterns, improvements
5. Generate review report with file:line references
6. Categorise findings (Critical, Important, Suggestion)

## Review Focus Areas

| Focus | Description | Checks |
|-------|-------------|--------|
| `patterns` | Design pattern adherence | SOLID, DRY, separation of concerns |
| `security` | Security vulnerabilities | Injection, auth, data exposure |
| `performance` | Performance issues | N+1 queries, memory leaks, blocking |
| `testing` | Test quality | Coverage, assertions, isolation |
| `all` | All areas (default) | Combined review |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--story` | Review specific story's code | next In Progress |
| `--file` | Review specific file | all story files |
| `--focus` | Review focus area | all |
| `--severity` | Minimum severity to report | all |

## Output

**Console report format:**

```markdown
## Code Review: US0001 - User Authentication

### Summary

| Category | Count |
|----------|-------|
| Critical | 1 |
| Important | 3 |
| Suggestions | 5 |

### Critical Issues

1. **SQL Injection Risk** - src/db/queries.ts:45
   - Raw string interpolation in SQL query
   - Fix: Use parameterised queries

### Important Issues

1. **Missing Error Handling** - src/api/handler.ts:78
   - Async operation without try-catch
   - Fix: Add error boundary

2. **Duplicated Validation Logic** - src/validators/user.ts:23, src/validators/admin.ts:45
   - Same email validation repeated
   - Fix: Extract to shared utility

3. **Overly Complex Method** - src/services/auth.ts:120-180
   - 60-line method with 4 levels of nesting
   - Fix: Consider extract-method refactoring

### Suggestions

1. **Consider Extract Method** - src/services/auth.ts:120-180
   - Method could be split for readability
   - See: /sdlc-studio code refactor --type extract-method

2. **Magic Number** - src/config.ts:34
   - `timeout: 30000` should be a named constant
   - Fix: `const DEFAULT_TIMEOUT_MS = 30000`
```

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| Critical | Security or correctness issue | Must fix before merge |
| Important | Maintainability or reliability | Should fix |
| Suggestion | Improvement opportunity | Consider fixing |

## Examples

```bash
# Review all code for next story
/sdlc-studio code review

# Review specific story
/sdlc-studio code review --story US0003

# Security-focused review
/sdlc-studio code review --focus security

# Review single file
/sdlc-studio code review --file src/auth/login.ts

# Show only critical and important issues
/sdlc-studio code review --severity important
```

## Next Steps

After review:

```bash
# Fix critical issues first
/sdlc-studio code refactor --type extract-method  # If suggested

# Re-run tests
/sdlc-studio code test --story US0001

# Verify AC still met
/sdlc-studio code verify --story US0001
```

## See Also

- `reference-refactor.md` - Review and refactoring workflows
- `/sdlc-studio code refactor help` - Guided refactoring
- `/sdlc-studio code check help` - Automated linting
- `best-practices/{language}.md` - Language-specific guidelines
