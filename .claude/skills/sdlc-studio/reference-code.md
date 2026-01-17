# SDLC Studio Code Reference

Detailed workflows for code planning, review, and quality checks.

---

# Detailed Workflows

## /sdlc-studio code plan - Step by Step

1. **Check Prerequisites**
   Verify stories exist:
   ```
   Glob: sdlc-studio/stories/US*.md
   ```
   If no stories found, prompt user to run `/sdlc-studio story` first.

2. **Select Story**
   - If `--story US0001` specified: use that story
   - If `--epic EP0001` specified: find next incomplete story in that epic
   - Otherwise: find next story with status Draft or Ready

   Read story file and parse:
   - Status (must be Draft or Ready)
   - Acceptance criteria (all AC sections)
   - Technical notes
   - Edge cases

3. **Detect Language**
   Check for project files in order:
   | File | Language | Framework |
   |------|----------|-----------|
   | `pyproject.toml` | Python | pytest |
   | `requirements.txt` | Python | pytest |
   | `package.json` + vitest | TypeScript | Vitest |
   | `package.json` | TypeScript | Jest |
   | `go.mod` | Go | testing |
   | `Cargo.toml` | Rust | cargo test |

4. **Load Best Practices**
   Read relevant best practices from `~/.claude/best-practices/`:
   - `python.md` for Python
   - `typescript.md` for TypeScript
   - `go.md` for Go
   - `rust.md` for Rust
   - Language-specific patterns and anti-patterns

5. **Explore Codebase**
   Use Task tool with Explore agent to understand:
   - Existing architecture patterns
   - Similar implementations to reference
   - Files likely to be modified
   - Testing conventions

6. **Generate Implementation Plan**
   Use sequential thinking to plan implementation:
   ```
   Use mcp__sequential-thinking__sequentialthinking to:
   1. Analyse each acceptance criterion
   2. Identify implementation phases
   3. Break into concrete steps with file changes
   4. Consider edge cases and error handling
   5. Plan test coverage
   6. Identify risks and dependencies
   ```

7. **Write Plan File**
   - Use template from `templates/plan-template.md`
   - Output to `sdlc-studio/plans/PL{NNNN}-{slug}.md`
   - Assign next available plan ID

8. **Update Plan Index**
   - Create or update `sdlc-studio/plans/_index.md`
   - Use template from `templates/plan-index-template.md`

9. **Update Story Status**
   Edit story file to change status:
   ```
   > **Status:** Draft  →  > **Status:** Planned
   ```
   or
   ```
   > **Status:** Ready  →  > **Status:** Planned
   ```

10. **Display Summary**
    Output to console:
    - Plan ID and file path
    - Story being planned
    - Number of implementation phases
    - Key files to modify
    - Next steps (run `/sdlc-studio code implement`)

---

## /sdlc-studio code implement - Step by Step

1. **Select Plan**
   - If `--plan PL0001` specified: use that plan
   - If `--story US0001` specified: find plan linked to that story
   - Otherwise: find next plan with status Draft for a Planned story

   Read plan file and parse:
   - Status (must be Draft)
   - Linked story (must be Planned status)
   - Implementation steps and phases
   - Recommended approach (TDD/Test-After/Hybrid)
   - Open questions

2. **Validate Prerequisites**
   - Plan exists and is Draft status
   - Story is in Planned status
   - No unresolved open questions (all checkboxes checked)

   If open questions remain unchecked:
   ```
   ## Cannot Proceed - Open Questions

   The following questions must be resolved before implementation:
   - [ ] Question 1
   - [ ] Question 2

   Please update the plan file and check off resolved questions.
   ```

3. **Determine Approach**
   Check plan's "Recommended Approach" section, then apply overrides:
   - `--tdd` flag → Force TDD mode
   - `--no-tdd` flag → Force Test-After mode
   - Neither → Use plan's recommendation

4. **Update Status**
   - Plan: `Draft` → `In Progress`
   - Story: `Planned` → `In Progress`

5. **Execute Implementation**
   Depending on approach:

   **TDD Mode:**
   For each acceptance criterion:
   1. Write failing test(s) covering the AC
   2. Run tests to verify they fail
   3. Implement minimal code to pass
   4. Run tests to verify they pass
   5. Refactor if needed
   6. Proceed to next AC

   **Test-After Mode:**
   1. Execute plan phases sequentially
   2. Follow implementation steps
   3. After all phases complete, write tests
   4. Verify all tests pass

6. **Documentation Updates (if --docs)**
   If `--docs` enabled (default: true):
   - Check plan's "Documentation Updates Required" section
   - Update each identified document
   - Add new sections or update existing content as needed

   If `--no-docs` specified, skip this step.

7. **Final Checks**
   Run quality checks:
   ```
   /sdlc-studio code check
   /sdlc-studio test --story {story_id}
   ```

8. **Complete Implementation**
   - Plan: `In Progress` → `Complete`
   - Display summary:
     ```
     ## Implementation Complete: US0001 - {title}

     ### Summary
     - Files created: 5
     - Files modified: 3
     - Tests added: 12
     - Documentation updated: 2 files

     ### Acceptance Criteria
     | AC | Status |
     |----|--------|
     | AC1 | Implemented |
     | AC2 | Implemented |
     | AC3 | Implemented |

     ### Next Steps
     Run `/sdlc-studio code review --story US0001` to verify implementation
     ```

---

## /sdlc-studio code review - Step by Step

1. **Select Story**
   - If `--story US0001` specified: use that story
   - If `--epic EP0001` specified: find next In Progress story in that epic
   - Otherwise: find next story with status In Progress

   Read story file and parse all acceptance criteria.

2. **Parse Acceptance Criteria**
   For each AC section, extract:
   - AC name/title
   - Given/When/Then conditions
   - Any additional requirements

3. **Explore Implementation**
   Use Task tool with Explore agent:
   ```
   Find implementation evidence for each acceptance criterion:
   - AC1: {ac1_description}
   - AC2: {ac2_description}
   ...
   Return file paths and line numbers where each AC is implemented.
   ```

4. **Verify Each Acceptance Criterion**
   For each AC:
   - Search for implementation code
   - Verify Given conditions are checked
   - Verify When actions are handled
   - Verify Then outcomes are produced
   - Document evidence (file:line references)

5. **Check Edge Cases**
   From story's Edge Cases section:
   - Verify each edge case is handled
   - Document where handling occurs

6. **Audit Best Practices**
   Check implementation against:
   - Language-specific best practices
   - Project coding standards
   - Security considerations
   - Error handling patterns

7. **Generate Report**
   Output console report:
   ```
   ## Code Review: US0001 - {title}

   ### Acceptance Criteria

   | AC | Status | Evidence |
   |----|--------|----------|
   | AC1: {name} | PASSED | src/auth.ts:45-67 |
   | AC2: {name} | FAILED | Not found |

   ### Edge Cases

   | Case | Status | Evidence |
   |------|--------|----------|
   | Empty input | PASSED | src/validate.ts:23 |

   ### Best Practices

   | Check | Status | Notes |
   |-------|--------|-------|
   | Error handling | PASSED | Uses custom errors |
   | Input validation | WARNING | Missing in 2 places |

   ### Summary
   - Passed: 5/6 acceptance criteria
   - Failed: 1/6 acceptance criteria
   - Recommendation: Address failed AC before marking complete
   ```

8. **Update Story Status (if all passed)**
   If all acceptance criteria met:
   ```
   > **Status:** In Progress  →  > **Status:** Review
   ```

---

## /sdlc-studio code check - Step by Step

1. **Detect Language**
   Same detection as code plan (see step 3 above).

2. **Select Linter Configuration**
   | Language | Linter | Config |
   |----------|--------|--------|
   | Python | ruff | pyproject.toml or ruff.toml |
   | TypeScript | eslint | eslint.config.js or .eslintrc |
   | Go | go fmt + go vet | - |
   | Rust | cargo clippy | - |

3. **Run Linters**
   Execute appropriate linter:
   - If `--no-fix`: run in check-only mode
   - Otherwise: run with auto-fix enabled

   | Language | Check Command | Fix Command |
   |----------|--------------|-------------|
   | Python | `ruff check .` | `ruff check --fix .` |
   | TypeScript | `npx eslint .` | `npx eslint --fix .` |
   | Go | `go fmt -n ./...` | `go fmt ./...` |
   | Rust | `cargo clippy` | `cargo clippy --fix` |

4. **Check Best Practices Anti-patterns**
   Load anti-patterns from best practices and search codebase:
   - TODO/FIXME comments
   - Hardcoded secrets
   - Disabled tests
   - Large functions (>50 lines)
   - Deep nesting (>4 levels)

5. **Generate Report**
   Output console report:
   ```
   ## Code Quality Check

   ### Linter Results

   | Type | Count | Auto-fixed |
   |------|-------|------------|
   | Errors | 3 | 2 |
   | Warnings | 7 | 5 |
   | Style | 12 | 12 |

   ### Files Modified
   - src/auth.ts (3 fixes)
   - src/utils.ts (2 fixes)

   ### Remaining Issues
   1. src/api.ts:45 - Unused variable 'response'
   2. src/db.ts:123 - Function too complex

   ### Anti-patterns Found
   - 3 TODO comments
   - 1 hardcoded timeout value

   ### Summary
   - 19 auto-fixed issues
   - 2 issues require manual attention
   ```

---

## /sdlc-studio test - Step by Step

1. **Parse Arguments**
   | Argument | Effect |
   |----------|--------|
   | (none) | Run all tests |
   | `--epic EP0001` | Filter by epic traceability |
   | `--story US0001` | Filter by story traceability |
   | `--spec TSP0001` | Filter by test spec |
   | `--type unit` | Filter by test type |
   | `--verbose` | Show detailed output |

2. **Detect Test Framework**
   Same detection as code plan (see step 3 above).

3. **Build Traceability Map (if filtered)**
   If filtering by epic/story/spec:
   - Read test spec files in `sdlc-studio/testing/specs/`
   - Extract test case IDs linked to stories
   - Map test cases to test file paths
   - Build list of tests to run

4. **Run Tests**
   Execute tests with appropriate framework:
   | Framework | Command |
   |-----------|---------|
   | pytest | `pytest {test_paths} -v` |
   | Vitest | `npx vitest run {test_paths}` |
   | Jest | `npx jest {test_paths}` |
   | Go | `go test {packages} -v` |
   | Rust | `cargo test {tests}` |

5. **Parse Results**
   Extract from test output:
   - Total tests run
   - Passed count
   - Failed count
   - Skipped count
   - Test names and status

6. **Map to Stories**
   Using traceability from test specs:
   - Group test results by story
   - Calculate coverage per story
   - Identify stories with failing tests

7. **Generate Report**
   Output console report:
   ```
   ## Test Results

   ### Summary
   | Metric | Value |
   |--------|-------|
   | Total | 45 |
   | Passed | 42 |
   | Failed | 2 |
   | Skipped | 1 |

   ### By Story

   | Story | Tests | Passed | Failed |
   |-------|-------|--------|--------|
   | US0001 | 12 | 12 | 0 |
   | US0002 | 8 | 6 | 2 |
   | US0003 | 10 | 10 | 0 |

   ### Failed Tests
   1. test_user_login_invalid_password
      - Story: US0002
      - Error: AssertionError: Expected 401, got 500

   2. test_user_login_rate_limit
      - Story: US0002
      - Error: Timeout after 5000ms
   ```

8. **Update Story Status (if applicable)**
   For stories in Review status with all tests passing:
   ```
   > **Status:** Review  →  > **Status:** Done
   ```

---

# Status Update Flow

```
Draft/Ready  ──[code plan]──▶  Planned
                                  │
                         [code implement]
                                  │
                                  ▼
                            In Progress
                                  │
                          [code review]
                                  │
                          (all AC met?)
                                  │
              ┌───────────────────┴───────────────────┐
              │ Yes                                    │ No
              ▼                                        ▼
         In Progress  ──▶  Review                Stay In Progress
                              │                    (fix issues)
                         [test passes]
                              │
                    (Review + all pass?)
                              │
              ┌───────────────┴───────────────┐
              │ Yes                            │ No
              ▼                                ▼
           Review  ──▶  Done              Stay Review
                                          (fix tests)
```

---

# Best Practices Integration

## Python Projects

Load from `~/.claude/best-practices/python.md`:
- Type hints required
- Docstrings for public functions
- Ruff formatting
- pytest conventions

## TypeScript Projects

Load from `~/.claude/best-practices/typescript.md`:
- Strict mode enabled
- ESLint + Prettier
- Jest/Vitest patterns
- Error handling

## Go Projects

Load from `~/.claude/best-practices/go.md`:
- Error wrapping
- Table-driven tests
- go fmt compliance

## Rust Projects

Load from `~/.claude/best-practices/rust.md`:
- Clippy compliance
- Error handling with Result
- Documentation comments

---

# Error Handling

## Code Plan Errors

| Condition | Action |
|-----------|--------|
| No stories exist | Prompt to run `/sdlc-studio story` |
| No incomplete stories | Report all stories complete |
| Story not found (--story) | Report error, list available stories |
| Epic not found (--epic) | Report error, list available epics |
| Unknown language | Ask user to specify framework |

## Code Implement Errors

| Condition | Action |
|-----------|--------|
| No plans exist | Prompt to run `/sdlc-studio code plan` |
| No Planned stories | Report no stories ready for implementation |
| Plan not found (--plan) | Report error, list available plans |
| Story not Planned status | Report wrong status, show current status |
| Unresolved open questions | List questions, pause for resolution |
| Tests fail during TDD | Report failure, prompt to fix |
| Documentation update fails | Report which doc failed, continue |

## Code Review Errors

| Condition | Action |
|-----------|--------|
| No In Progress stories | Report no stories ready for review |
| Story not found | Report error, list available stories |
| No implementation found | Report AC as FAILED with "Not found" |

## Code Check Errors

| Condition | Action |
|-----------|--------|
| Linter not installed | Report error, suggest install command |
| No config found | Use default config |
| Linter fails | Report errors to user |

## Test Errors

| Condition | Action |
|-----------|--------|
| Test framework not found | Report error, suggest install |
| No tests match filter | Report no matching tests |
| Tests fail | Report failures, do not update status |
