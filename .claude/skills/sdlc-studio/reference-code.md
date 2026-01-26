# SDLC Studio Code Reference

Detailed workflows for code planning, review, and quality checks.

---

# Detailed Workflows {#detailed-workflows}

## /sdlc-studio code plan - Step by Step {#code-plan-workflow}

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
   Check for project files to detect language and framework.

   > **Detection table:** `reference-testing.md` → Detect Language

4. **Load Best Practices**
   Read relevant best practices from `~/.claude/best-practices/`:
   - `python.md` for Python
   - `typescript.md` for TypeScript
   - `go.md` for Go
   - `rust.md` for Rust
   - Language-specific patterns and anti-patterns

5. **Enforce Edge Case Coverage (MANDATORY)** {#edge-case-coverage}

   Every edge case from the Story MUST have a handling strategy:

   a) Extract all edge cases from Story's "Edge Cases & Error Handling" section
   b) For each edge case, document:
      - Handling Strategy (how it will be addressed)
      - Implementation Phase (when it will be implemented)
   c) Validate coverage:
      ```
      Story edge cases: N
      Handled in plan: N (must equal story count)
      Unhandled: 0 (must be zero to proceed)
      ```
   d) If any edge cases are unhandled, the plan CANNOT be written

   **Plan template section to populate:**
   ```markdown
   ## Edge Case Handling Plan

   | # | Edge Case (from Story) | Handling Strategy | Phase |
   |---|------------------------|-------------------|-------|
   | 1 | Empty input            | Return 400 with validation error | Phase 1 |
   | 2 | Network timeout        | Retry 3x with exponential backoff | Phase 2 |
   ```

6. **Explore Codebase**
   Use Task tool with Explore agent to understand:
   - Existing architecture patterns
   - Similar implementations to reference
   - Files likely to be modified
   - Testing conventions

7. **Generate Implementation Plan**
   Use sequential thinking to plan implementation:
   ```
   Use mcp__sequential-thinking__sequentialthinking to:
   1. Analyse each acceptance criterion
   2. Identify implementation phases
   3. Break into concrete steps with file changes
   4. Map edge cases to handling strategies (validated in step 5)
   5. Plan test coverage
   6. Identify risks and dependencies
   7. Determine TDD vs Test-After recommendation
   ```

8. **Write Plan File**
   - Use template from `templates/plan-template.md`
   - Output to `sdlc-studio/plans/PL{NNNN}-{slug}.md`
   - Assign next available plan ID

9. **Update Plan Index**
   - Create or update `sdlc-studio/plans/_index.md`
   - Use template from `templates/plan-index-template.md`

10. **Update Story Status**
    Edit story file to change status:
    ```
    > **Status:** Draft  →  > **Status:** Planned
    ```
    or
    ```
    > **Status:** Ready  →  > **Status:** Planned
    ```

11. **Display Summary**
    Output to console:
    - Plan ID and file path
    - Story being planned
    - Number of implementation phases
    - Key files to modify
    - Next steps (run `/sdlc-studio code implement`)

---

## /sdlc-studio code implement - Step by Step {#code-implementation-workflow}

**CRITICAL REQUIREMENT: Complete ALL plan phases.**

Do NOT pause mid-implementation to ask questions like "Would you like me to continue with the frontend?" or "Should I implement this now?". Execute EVERY phase from the plan (backend, frontend, integration, database, etc.) in sequence before marking the implementation complete.

If you encounter uncertainty during implementation:
- Make a reasonable choice based on existing patterns
- Document the decision in code comments if non-obvious
- Continue to the next phase
- Only stop if there's a blocking error (tests fail, code won't compile)

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

3. **Check Best Practices and Library Documentation**

   **This step is mandatory before writing any code.**

   a) Read the relevant best practice guide:
      - Python: `~/.claude/best-practices/python.md`
      - TypeScript: `~/.claude/best-practices/typescript.md`
      - Go: `~/.claude/best-practices/go.md`

   b) Query Context7 for each external library in the plan's "Library Documentation" section:
      ```
      mcp__context7__resolve-library-id({ libraryName: "fastapi", query: "feature needed" })
      mcp__context7__query-docs({ libraryId: "/tiangolo/fastapi", query: "specific pattern" })
      ```

   c) Update plan with key patterns discovered (if significant):
      - Add to "Key Patterns" column in Library Documentation table
      - Note any API changes from expected patterns

4. **Verify API Contracts (if applicable)**

   **This step is mandatory when writing code that consumes an API.**

   If the implementation involves calling backend APIs, database queries, or external services:

   a) Find and read the actual schema/contract:
      - Backend API: Check schema files (e.g., `src/**/schemas/*.py`, `src/**/types/*.ts`)
      - Database: Check migration files or ORM models
      - External API: Check OpenAPI spec or official documentation

   b) Verify against the running system:
      ```bash
      # For REST APIs - actually call the endpoint
      curl -s http://localhost:PORT/api/endpoint | jq '.'
      ```

   c) Update TypeScript/frontend types to match EXACTLY what the API returns
      - Do not invent fields that don't exist in the response
      - Do not assume field names - verify them

   **Why this matters:** Unit tests only verify code matches expectations. If expectations are wrong (invented API fields), tests pass but the code fails against the real system.

5. **Determine Approach**
   Check plan's "Recommended Approach" section, then apply overrides:
   - `--tdd` flag → Force TDD mode
   - `--no-tdd` flag → Force Test-After mode
   - Neither → Use plan's recommendation

6. **Update Status**
   - Plan: `Draft` → `In Progress`
   - Story: `Planned` → `In Progress`

7. **Execute Implementation**
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
   1. Execute ALL plan phases sequentially (do NOT skip any phase)
   2. Follow implementation steps for each phase (backend, frontend, etc.)
   3. After ALL phases are complete, write tests
   4. Verify all tests pass

   **Completion check:** Before proceeding to step 3, verify every phase in the plan's "Implementation Phases" section has been executed. If a phase is incomplete, go back and complete it.

8. **Documentation Updates (if --docs)**
   If `--docs` enabled (default: true):
   - Check plan's "Documentation Updates Required" section
   - Update each identified document
   - Add new sections or update existing content as needed

   If `--no-docs` specified, skip this step.

9. **Final Checks**
   Run quality checks:
   ```
   /sdlc-studio code check
   /sdlc-studio code test --story {story_id}
   ```

   **Warning Policy (mandatory):**
   - Tests MUST pass with warnings treated as errors
   - For pytest: `pytest -W error`
   - DO NOT dismiss warnings - investigate and fix root cause

   > **Full guidance:** `reference-test-best-practices.md` → Warning Policy

   **Manual Verification (mandatory):**
   - If changes involve UI: open the application in a browser and test the feature
   - If changes involve API: curl the endpoint and verify the response
   - If changes involve CLI: run the command and verify output
   - Rebuild containers if using Docker: `docker compose build && docker compose up -d`

   **Unit tests passing is not sufficient.** Tests verify code matches expectations, but expectations can be wrong. Manual verification against the running system is the only way to confirm the implementation actually works.

10. **Validate All Phases Complete**
   Before marking complete, verify:
   - [ ] Every phase from "Implementation Phases" has been executed
   - [ ] All acceptance criteria have implementing code
   - [ ] Backend, frontend, and integration work (if in plan) are done
   - [ ] No phases marked as "pending" or "TODO"

   If any phase is incomplete, go back and complete it before proceeding.

11. **Complete Implementation**
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
     Run `/sdlc-studio code verify --story US0001` to verify implementation
     ```

---

## /sdlc-studio code verify - Step by Step {#code-verify-workflow}

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
   ## Code Verification: US0001 - {title}

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

## /sdlc-studio code check - Step by Step {#code-check-workflow}

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

## /sdlc-studio code test - Step by Step {#code-test-workflow}

1. **Parse Arguments**
   | Argument | Effect |
   |----------|--------|
   | (none) | Run all tests |
   | `--epic EP0001` | Filter by epic traceability |
   | `--story US0001` | Filter by story traceability |
   | `--spec TS0001` | Filter by test spec |
   | `--type unit` | Filter by test type |
   | `--verbose` | Show detailed output |

2. **Detect Test Framework**
   Same detection as code plan (see step 3 above).

3. **Build Traceability Map (if filtered)**
   If filtering by epic/story/spec:
   - Read test spec files in `sdlc-studio/test-specs/`
   - Extract test case IDs linked to stories
   - Map test cases to test file paths
   - Build list of tests to run

4. **Run Tests**
   Execute tests with appropriate framework:
   | Framework | Command |
   |-----------|---------|
   | pytest | `pytest {test_paths} -v -W error` |
   | Vitest | `npx vitest run {test_paths}` |
   | Jest | `npx jest {test_paths}` |
   | Go | `go test {packages} -v` |
   | Rust | `cargo test {tests}` |

   **Warning Policy:**
   - All frameworks: Warnings MUST be treated as errors
   - pytest: Use `-W error` to fail on any warning
   - If warnings occur, fix the root cause before proceeding
   - Never dismiss warnings as acceptable - they indicate quality issues

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

9. **Propagate Results (Backward Traceability)**

   Test results MUST update related artifacts for traceability:

   a) **Update Test-Spec automation status:**
      - For each test case executed, update Automation Status table
      - Mark as "Pass", "Fail", or "Skip" with timestamp

   b) **Update Story AC status based on test results:**
      - Map test failures to specific ACs using TC→AC mapping
      - If all tests for an AC pass → AC remains verified
      - If any test for an AC fails → AC marked as Regression

   c) **Story status changes:**
      | Test Result | Story in Done | Story in Review |
      |-------------|---------------|-----------------|
      | All pass | Remains Done | → Done |
      | Any fail | → **Regression** | Remains Review |

   d) **Auto-create Bug on failure (optional, with --create-bugs):**
      ```markdown
      ## Auto-generated Bug

      **Title:** Test failure: {test_name}
      **Affected Story:** US{NNNN}
      **Affected AC:** AC{N}
      **Test Case:** TC{NNNN}
      **Error:** {assertion_error}
      ```

   e) **Update _index files:**
      - Stories _index: Update status counts
      - Test-specs _index: Update pass/fail counts

---

# TDD vs Test-After {#tdd-vs-test-after}

> **Source of truth:** `reference-decisions.md` → TDD vs Test-After Decision Tree

For the complete decision tree, conditions for TDD vs Test-After, and override flags, see `reference-decisions.md`.

---

# Status Update Flow {#status-update-flow}

```
Draft/Ready  ──[code plan]──▶  Planned
                                  │
                         [code implement]
                                  │
                                  ▼
                            In Progress
                                  │
                          [code verify]
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

# Best Practices Integration {#best-practices-integration}

## Python Projects {#python-projects}

Load from `~/.claude/best-practices/python.md`:
- Type hints required
- Docstrings for public functions
- Ruff formatting
- pytest conventions

## TypeScript Projects {#typescript-projects}

Load from `~/.claude/best-practices/typescript.md`:
- Strict mode enabled
- ESLint + Prettier
- Jest/Vitest patterns
- Error handling

## Go Projects {#go-projects}

Load from `~/.claude/best-practices/go.md`:
- Error wrapping
- Table-driven tests
- go fmt compliance

## Rust Projects {#rust-projects}

Load from `~/.claude/best-practices/rust.md`:
- Clippy compliance
- Error handling with Result
- Documentation comments

---

# Error Handling {#error-handling}

## Code Plan Errors {#code-plan-errors}

| Condition | Action |
|-----------|--------|
| No stories exist | Prompt to run `/sdlc-studio story` |
| No incomplete stories | Report all stories complete |
| Story not found (--story) | Report error, list available stories |
| Epic not found (--epic) | Report error, list available epics |
| Unknown language | Ask user to specify framework |

## Code Implement Errors {#code-implement-errors}

| Condition | Action |
|-----------|--------|
| No plans exist | Prompt to run `/sdlc-studio code plan` |
| No Planned stories | Report no stories ready for implementation |
| Plan not found (--plan) | Report error, list available plans |
| Story not Planned status | Report wrong status, show current status |
| Unresolved open questions | List questions, pause for resolution |
| Tests fail during TDD | Report failure, prompt to fix |
| Documentation update fails | Report which doc failed, continue |
| API contract not verified | Read backend schema before writing frontend code |
| Manual verification fails | Fix code, do not mark implementation complete |
| Invented API fields | Check actual API response, update types to match reality |

## Code Review Errors {#code-review-errors}

| Condition | Action |
|-----------|--------|
| No In Progress stories | Report no stories ready for review |
| Story not found | Report error, list available stories |
| No implementation found | Report AC as FAILED with "Not found" |

## Code Check Errors {#code-check-errors}

| Condition | Action |
|-----------|--------|
| Linter not installed | Report error, suggest install command |
| No config found | Use default config |
| Linter fails | Report errors to user |

## Test Errors {#test-errors}

| Condition | Action |
|-----------|--------|
| Test framework not found | Report error, suggest install |
| No tests match filter | Report no matching tests |
| Tests fail | Report failures, do not update status |

---

# Workflow Orchestration {#workflow-orchestration}

> **Source of truth:** `reference-story.md` and `reference-epic.md`

For automated story and epic workflows:
- Story workflows: `reference-story.md` → Workflow Commands
- Epic workflows: `reference-epic.md` → Workflow Commands

---

# See Also

- `reference-decisions.md` - Decision impact matrix, TDD decision tree, Ready criteria
- `reference-prd.md, reference-trd.md, reference-persona.md` - PRD, TRD, Persona workflows
- `reference-epic.md, reference-story.md, reference-bug.md` - Epic, Story, Bug workflows
- `reference-testing.md` - Test Strategy, Spec, Automation workflows
- `reference-philosophy.md` - Create vs Generate philosophy
- `reference-test-best-practices.md` - Test generation pitfalls and validation
- `reference-test-e2e-guidelines.md` - E2E and mocking patterns

---

## Navigation {#navigation}

**Prerequisites (load these first):**
- `reference-story.md` - User Stories (must exist and be Ready before code planning)
- `reference-decisions.md#story-ready` - Ready criteria for stories

**Related workflows:**
- `reference-testing.md` - Test workflows (parallel - tests accompany code)
- `reference-test-best-practices.md` - Test quality guidelines
- `reference-test-e2e-guidelines.md` - E2E testing patterns

**Cross-cutting concerns:**
- `reference-decisions.md` - Decision guidance and Ready criteria
- `reference-outputs.md#output-formats` - File formats and status values

**Deep dives (optional):**
- `reference-trd.md` - Technical architecture context
- `reference-philosophy.md` - Create vs Generate philosophy
