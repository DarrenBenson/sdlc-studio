# SDLC Studio Reference - Story

Detailed workflows for User Story generation, quality enforcement, and management.

<!-- Load when: generating or managing Stories -->

## Reading Guide

| Section | When to Read |
|---------|--------------|
| Story Workflows | When generating stories from epics |
| Story Generate Workflow | When extracting specs from existing code |
| Story Quality Enforcement | When validating story readiness |
| Workflow Commands | When using `story plan` or `story implement` |
| Section Reference | See `reference-story-sections.md` for template guidance |

---

# Story Workflows

## /sdlc-studio story - Step by Step {#story-workflow}

1. **Check Prerequisites**
   - Check sdlc-studio/personas.md exists
     - If missing: create from template, ask user to populate, STOP
   - Check sdlc-studio/epics/ has epic files
     - If empty: prompt to run `/sdlc-studio epic` first, STOP
   - Create sdlc-studio/stories/ if needed
   - Scan for existing stories to determine next ID

2. **Parse Inputs**
   - Read personas (name, role, goals, pain points)
   - Read Epic(s) to process
   - For each Epic, extract:
     - Acceptance criteria
     - Scope
     - Affected personas
     - Technical considerations

3. **Break Down into Stories**
   For each Epic:
   - Identify atomic user actions
   - Apply heuristics:
     - One story per distinct action
     - Completable in one sprint
     - Split by persona when relevant
   - For each story:
     a. Select most relevant persona
     b. Write "As a... I want... So that..."
     c. Generate 3-5 Given/When/Then criteria
     d. Identify edge cases
     e. Leave Story Points as {{TBD}}
     f. **Detect cross-story dependencies** (see step 3b)

3b. **Detect Cross-Story Dependencies (MANDATORY)**

   Automatically identify dependencies between stories:

   a) **Schema Dependencies:**
      - Scan story for config schemas, data models, or types
      - Check if any schema is defined in another story
      - If found, add to Schema Dependencies table

   b) **API Dependencies:**
      - Scan story for API endpoint consumption
      - Check if endpoint is defined in another story
      - If found, add to API Dependencies table

   c) **Service Dependencies:**
      - Scan story for service/function calls
      - Check if service is defined in another story
      - If found, add to Story Dependencies table

   d) **Populate story template sections:**
      ```markdown
      ### Story Dependencies
      | Story | Dependency Type | What's Needed | Status |
      |-------|-----------------|---------------|--------|
      | US0013 | Schema | NotificationsConfig | Done |

      ### Schema Dependencies
      | Schema | Source Story | Fields Needed |
      |--------|--------------|---------------|
      | NotificationsConfig | US0013 | slack_webhook_url, notify_on_critical |

      ### API Dependencies
      | Endpoint | Source Story | How Used |
      |----------|--------------|----------|
      | GET /api/settings | US0023 | Fetch user preferences |
      ```

   e) **Warn if dependent story not Done:**
      ```
      > **Warning:** This story depends on stories that are not Done:
      > - US0013: Slack Notifications (In Progress)
      ```

4. **Generate Story Files**
   - Assign ID: US{NNNN} (global)
   - Create slug (kebab-case)
   - Use `templates/core/story.md`
   - Link to parent Epic

5. **Update Epic Files**
   - Add story links to Story Breakdown section
   - Update Estimated Story Count

6. **Write Files**
   - Write `sdlc-studio/stories/US{NNNN}-{slug}.md`
   - Create/update `sdlc-studio/stories/_index.md`
   - Update modified Epic files

7. **Report**
   - Stories created per Epic
   - Full story list
   - Criteria that couldn't be converted

8. **Run Cohesion Review (Automatic)**
   - See [Story Cohesion Review](#story-cohesion-review) below
   - Validates generated stories collectively cover the epic
   - Reports gaps, sizing issues, overlaps
   - Auto-fixes where possible

9. **Persona Validation (Optional)**
   Unless `--skip-personas` flag used:
   - For each story, identify the primary persona (from "As a...")
   - Offer: "Would you like persona validation of acceptance criteria?"
   - If yes, for each story:
     - Consult the story's persona about AC completeness
     - Run: `/sdlc-studio consult [persona] [story-file] --quick`
   - Report persona feedback:
     - AC that personas approved
     - AC that personas questioned
     - Missing scenarios personas identified
   - Optionally update stories with persona-suggested improvements

---

## Story Cohesion Review (Post-Generation) {#story-cohesion-review}

Automatic review that runs as the final step of story generation. Ensures stories collectively cover the epic requirements.

### Trigger

Runs automatically after `story generate --epic EP0001`. No separate command needed.

### Cohesion Checks

| Check | Description | Severity |
|-------|-------------|----------|
| **AC Coverage** | Every epic AC maps to at least one story AC | Critical |
| **Edge Cases** | All epic edge cases distributed across stories | Important |
| **Dependencies** | Story dependencies form valid DAG (no cycles) | Critical |
| **Sizing** | No story too large (> 13 points or > 10 AC) | Important |
| **Overlaps** | No duplicate AC across multiple stories | Suggestion |
| **Gaps** | No epic requirements left unaddressed | Critical |

### Cohesion Review Workflow {#cohesion-workflow}

```text
1. Gather Generated Stories
   - Load all stories just created for epic
   - Build story-to-AC mapping

2. Check AC Coverage
   - Parse epic AC list
   - For each epic AC: find matching story AC
   - Flag any epic AC with no story coverage

3. Check Edge Cases
   - Parse epic edge cases
   - For each: find story that handles it
   - Flag unhandled edge cases

4. Check Dependencies
   - Build dependency graph from story deps
   - Detect cycles (error if found)
   - Check schema/API deps have source stories

5. Check Sizing
   - Flag stories with > 13 points
   - Flag stories with > 10 AC
   - Suggest splitting if found

6. Check Overlaps
   - Compare AC text across stories
   - Flag similar AC in different stories
   - Suggest consolidation if overlap > 70%

7. Report & Auto-Fix
   - Display cohesion summary
   - If issues found:
     - Critical: Missing AC coverage, cycles
     - Important: Sizing issues, edge case gaps
     - Suggestion: Overlaps, dependency optimisations
   - Apply auto-fixes where safe
   - Update epic with discovered gaps
```

### Cohesion Report Output {#cohesion-output}

Displayed after story generation completes:

```text
## Story Cohesion Review: EP0001

Generated 6 stories for "User Authentication"

### AC Coverage                    ✅ 100%
All 12 epic AC mapped to story AC

### Edge Cases                     ⚠️ 1 gap
- "Rate limiting bypass" not covered → Added to US0006

### Dependencies                   ✅ Valid
No cycles, all deps have sources

### Sizing                         ⚠️ 1 flag
- US0003 has 14 AC → Consider splitting

### Overlaps                       ✅ None
No duplicate AC detected

### Actions Taken
- Added edge case to US0006
- Updated EP0001 open questions with sizing concern
```

### Auto-Fix Behaviour {#cohesion-auto-fix}

| Issue | Auto-Fix | Manual Action |
|-------|----------|---------------|
| Missing edge case | Add to most relevant story | None needed |
| Missing AC coverage | Add as open question on epic | User must assign to story |
| Cycle detected | Report error, no auto-fix | User must resolve |
| Oversized story | Add splitting suggestion to story | User decides whether to split |
| Overlapping AC | Report only, no auto-fix | User consolidates if needed |

### Cohesion Findings Storage {#cohesion-storage}

Cohesion review results are stored as part of the review findings system:

- **Location:** `sdlc-studio/reviews/RV{NNNN}-{epic-id}-cohesion.md`
- **Template:** `templates/review-findings-template.md` (cohesion section)
- **State tracking:** Updated in `sdlc-studio/.local/review-state.json`

---

## /sdlc-studio story review - Step by Step {#story-review-workflow}

1. **Load Stories**
   - Read all from sdlc-studio/stories/
   - Parse acceptance criteria and DoD items

2. **Analyse Implementation**
   For each story, use Task tool with Explore agent:
   ```
   For story [Title], check implementation:
   1. Code matching acceptance criteria
   2. Relevant test files
   3. API/UI implementation
   4. Documentation updates
   Assess: Which criteria are met?
   ```

3. **Update Story Files**
   - Update Status field
   - Check off completed criteria
   - Check off applicable DoD items
   - Add revision history entry
   - **"Done" rules:**
     - If all AC and DoD items met → suggest "Done" (user confirms)
     - "Done" is always a user decision, never auto-assigned
     - Prompt user: "All criteria complete. Mark story as Done? [y/N]"
     - **If user confirms Done:** Execute the **Story Completion Cascade** immediately.
       > **Canonical checklist:** `reference-outputs.md` → [Story Completion Cascade](#story-completion-cascade)

4. **Update Related Files**
   - Update _index.md with status counts
   - Check if Epic should be reviewed

5. **Report**
   - Stories completed
   - Stories in progress
   - Stories blocked
   - Regressions

---

## /sdlc-studio story generate - Step by Step (Specification Extraction) {#story-generate-workflow}

**Purpose:** Extract detailed, testable specifications from existing code. The output must be detailed enough that another team could rebuild the system without seeing the original code.

**See `reference-philosophy.md` for the full philosophy on Create vs Generate modes.**

1. **Check Prerequisites**
   - Check sdlc-studio/personas.md exists
   - Check sdlc-studio/epics/ has epic files for scope
   - Create sdlc-studio/stories/ if needed
   - Scan for existing stories to determine next ID

2. **Read Epic for Scope**
   - Load the target Epic(s)
   - Extract: features to cover, affected endpoints, components

3. **Deep Code Exploration**
   Use Task tool with Explore agent:
   ```
   For Epic [Title], extract implementation specifications:

   1. Find all implementing code (routes, services, models)
   2. For each endpoint/function:
      - Exact request/response shapes
      - All validation rules with actual error messages
      - Edge cases handled in code
      - Default values and limits
   3. Document actual behaviour, not assumed behaviour

   Return: Structured specification per feature
   ```

4. **Generate Implementation-Ready Stories**
   For each feature identified:

   a. **Write precise AC** - not "returns data" but exact shapes:
      ```
      - Given an engram exists with slug "test-person"
      - When I GET /engrams/test-person
      - Then I receive 200 with JSON containing:
        - slug: "test-person"
        - name: string (extracted from engram file)
        - role: string
        - category: "fictional" or "real"
        - el_rating: string or null
        - engram_content: string (full .engram file)
        - psychometrics: object or null
        - user_manual: string or null
        - labels: array of strings
      ```

   b. **Document all edge cases** with specific inputs and outputs:
      ```
      | Scenario | Input | Expected |
      |----------|-------|----------|
      | Not found | GET /engrams/nonexistent | 404, {"detail": "Engram not found: nonexistent"} |
      | Invalid slug chars | GET /engrams/has spaces | 404 or 422 depending on routing |
      ```

   c. **Extract actual validation rules** from code:
      - What fields are required?
      - What are the length limits?
      - What values are allowed?
      - What are the exact error messages?

   d. **Document API contracts precisely**:
      - Request method, path, headers required
      - Request body schema with types
      - Response codes and their meanings
      - Response body schemas for each code

5. **Set Status to Ready (NOT Done)**
   - Generated specs await validation
   - Done only after tests pass against implementation

6. **Write Story Files**
   - Use `templates/core/story.md`
   - Include exhaustive edge case tables
   - Include precise API contracts
   - Link to parent Epic

7. **Update Registries**
   - Update `sdlc-studio/stories/_index.md`
   - Update Epic with story links

8. **Report with Next Steps**
   - Stories generated
   - Remind: specs are NOT validated until tests pass
   - Suggest: `/sdlc-studio test-spec --epic EP00XX` next

**Quality Checklist for Generated Stories:**
- [ ] AC detailed enough to implement without seeing original code
- [ ] All edge cases documented with specific inputs/outputs
- [ ] API contracts include exact request/response shapes
- [ ] Error scenarios include actual error messages from code
- [ ] No ambiguous language ("handles errors", "returns data")
- [ ] Validation rules extracted from actual code

---

# Story Quality Enforcement

Before marking a story as Ready, verify it meets minimum standards.

> **Ready criteria:** `reference-decisions.md` → Story Ready

## Story Ready Validation (Enforced) {#ready-validation}

Stories CANNOT be marked Ready unless they meet these enforced minimums:

### API Stories {#api-stories}

| Requirement | Minimum | Enforcement |
|-------------|---------|-------------|
| Edge cases documented | 8 | Count `\| Scenario` rows in edge case table |
| Test scenarios listed | 10 | Count `- [ ]` items in Test Scenarios section |
| Given/When/Then concrete | All AC | No placeholders or TBD |
| Error codes specified | All errors | Each error has code and message |
| Open questions resolved | All critical | No unresolved critical questions |

### UI Stories {#ui-stories}

| Requirement | Minimum | Enforcement |
|-------------|---------|-------------|
| Edge cases documented | 5 | Count `\| Scenario` rows |
| Test scenarios listed | 8 | Count `- [ ]` items |
| UI states documented | All | Loading, error, empty, success |
| Accessibility noted | Required | Screen reader, keyboard nav |
| Open questions resolved | All critical | No unresolved critical |

### Validation Algorithm {#validation-algorithm}

```python
def validate_story_ready(story):
    errors = []

    # Count edge cases
    edge_cases = count_table_rows(story, "Edge Cases")
    min_edge_cases = 8 if story.is_api else 5
    if edge_cases < min_edge_cases:
        errors.append(f"Edge cases: {edge_cases}/{min_edge_cases} (need {min_edge_cases - edge_cases} more)")

    # Count test scenarios
    test_scenarios = count_checkboxes(story, "Test Scenarios")
    min_scenarios = 10 if story.is_api else 8
    if test_scenarios < min_scenarios:
        errors.append(f"Test scenarios: {test_scenarios}/{min_scenarios}")

    # Check for placeholders
    if contains_placeholder(story.acceptance_criteria):
        errors.append("AC contains TBD or placeholder text")

    # Check critical open questions
    critical_questions = get_unresolved_critical(story.open_questions)
    if critical_questions:
        errors.append(f"Unresolved critical questions: {len(critical_questions)}")

    # Check ambiguous language
    ambiguous = detect_ambiguous_language(story)
    if ambiguous:
        errors.append(f"Ambiguous language found: {', '.join(ambiguous)}")

    return errors
```

### Validation Output {#validation-output}

When attempting to mark a story Ready:

```markdown
## Story Ready Validation: US0024

### Status: BLOCKED

Cannot mark Ready - the following requirements are not met:

| Requirement | Current | Required | Gap |
|-------------|---------|----------|-----|
| Edge cases | 5 | 8 | Need 3 more |
| Test scenarios | 7 | 10 | Need 3 more |
| Critical questions | 2 unresolved | 0 | Resolve or downgrade |

### Ambiguous Language Detected

The following phrases should be made specific:

| Location | Phrase | Suggestion |
|----------|--------|------------|
| AC2 | "handles errors" | Specify which errors and how |
| Edge Case 3 | "returns appropriate response" | Specify exact response |

### Actions Required

1. Add 3 more edge cases to Edge Cases table
2. Add 3 more test scenarios to Test Scenarios section
3. Resolve or downgrade critical open questions
4. Replace ambiguous language with specific behaviour
```

## Quality Checklist {#quality-checklist}

### All Stories {#all-stories}

- [ ] No ambiguous language ("handles errors", "returns data", "works correctly")
- [ ] All Open Questions have target resolution dates
- [ ] Critical Open Questions resolved before Ready status
- [ ] Given/When/Then uses concrete values, not placeholders
- [ ] Persona referenced with specific context (not just name)

## Blocking Conditions {#blocking-conditions}

**Do NOT mark Ready if:**

| Condition | Why It Blocks |
|-----------|---------------|
| Critical Open Question unresolved | Specification incomplete |
| Edge case count below 8 (API stories) | Test coverage will have gaps |
| API contracts use vague language | Implementer will make assumptions |
| "TBD" still in acceptance criteria | Story is not actually ready |
| No error scenarios documented | Happy-path-only specification |

## Ambiguous Language Detection {#ambiguous-language-detection}

> **Source of truth:** `reference-decisions.md` → Ambiguous Language Detection

These phrases indicate specification gaps. Replace before marking Ready.

## Quality Metrics {#quality-metrics}

Track story quality across the project:

```
/sdlc-studio status --quality

Story Quality:
  Total: 24 stories
  Ready: 18 (12 high-quality, 6 need improvement)
  Draft: 6

  Edge case coverage: 85% meet minimum
  Ambiguous language: 3 stories flagged
  Open Questions: 2 unresolved critical
```

---

# User Story Section Reference

> **Section-by-section guidance:** See `reference-story-sections.md` for detailed guidance on completing each section of the story template (User Story statement, Context, AC, Scope, UI/UX, Technical Notes, Edge Cases, Test Scenarios, DoD, Estimation).

---

# Workflow Commands

Automated workflows for complete story implementation.

These commands operate on a single story. For autonomous epic-level execution with concurrent waves, see `reference-epic.md#flag-agentic`.

## /sdlc-studio story plan - Step by Step {#story-plan-workflow}

1. **Validate Story Ready**
   - Load story file from sdlc-studio/stories/
   - Check status is Ready (not Draft, Planned, or Done)
   - Verify all Ready criteria met (see reference-decisions.md):
     - All AC in Given/When/Then format
     - No TBD or placeholder text
     - Edge cases complete (minimum 8 for API, 5 for others)
     - No ambiguous language
     - Critical Open Questions resolved

2. **Check Dependencies**
   - Parse story Dependencies section
   - For each dependent story, verify status is Done
   - If any dependency not Done, report warning:
     ```
     > **Warning:** This story depends on stories that are not Done:
     > - US0013: Slack Notifications (In Progress)
     ```

3. **Determine Approach**
   Apply TDD decision tree from reference-decisions.md:

   | Factor | TDD | Test-After |
   |--------|-----|------------|
   | Edge cases >5 | Yes | |
   | Clear AC | Yes | |
   | API story | Yes | |
   | UI-heavy | | Yes |
   | Exploratory | | Yes |
   | Complex business rules | Yes | |

   Document rationale for approach selection.

4. **Create Implementation Plan (MANDATORY)**
   - Run `code plan --story US000X` internally
   - Write plan file to `sdlc-studio/plans/PL{NNNN}-{slug}.md`
   - **STOP if file creation fails** - do not proceed without written plan
   - Store plan ID for workflow tracking

5. **Create Test Specification (MANDATORY)**
   - Run `test-spec --story US000X` internally
   - Write spec file to `sdlc-studio/test-specs/TS{NNNN}-{slug}.md`
   - **STOP if file creation fails** - do not proceed without written spec
   - Store spec ID for workflow tracking

6. **Review Created Artifacts with User**
   Present the created artifacts for user review:
   ```
   ## Story Workflow Plan: US0024

   **Story:** Action Queue API Endpoint
   **Status:** Ready → Planned
   **Dependencies:** US0023 (Done)

   ### Artifacts Created

   | Artifact | Path | Status |
   |----------|------|--------|
   | Implementation Plan | sdlc-studio/plans/PL0024-action-queue-api.md | ✅ Created |
   | Test Specification | sdlc-studio/test-specs/TS0024-action-queue-api.md | ✅ Created |

   ### Approach: TDD
   Reason: API story with 8 edge cases, clear Given/When/Then AC

   ### Execution Phases

   | Phase | Command | Artifacts |
   |-------|---------|-----------|
   | 1. Plan | ✅ Complete | PL0024-action-queue-api.md |
   | 2. Test Spec | ✅ Complete | TS0024-action-queue-api.md |
   | 3. Tests | test-automation | tests/test_action_queue_api.py |
   | 4. Implement | code implement | src/api/action_queue.py |
   | 5. Test | code test | Run tests |
   | 6. Verify | code verify | Verify against AC |
   | 7. Check | code check | Quality gates |
   | 8. Review | status | Final status review |

   Review the plan and test-spec files. Ready to continue?
   Run: /sdlc-studio story implement --story US0024
   ```

   **CRITICAL:** Steps 4 and 5 MUST complete with files written to disk before showing this review. If no files exist, the workflow has failed.

---

## /sdlc-studio story implement - Step by Step {#story-implement-workflow}

1. **Check for Existing Workflow State (MANDATORY RESUME CHECK)**

   **CRITICAL:** Before starting any work, check if this story has an existing workflow:

   a. Search for workflow file: `sdlc-studio/workflows/WF*-{story-slug}.md`

   b. **If workflow exists:**
      - Read the workflow state file
      - Check "Current Phase" and "Phase Progress" table
      - Identify last completed phase and any errors
      - Report resume status to user:
        ```
        ## Resuming Workflow: WF0024

        **Story:** US0024 - Action Queue API
        **Last Session:** 2026-01-27
        **Completed Phases:** 1-3 (Plan, Test Spec, Implement)
        **Resume From:** Phase 4 (Tests)

        Continuing from where we left off...
        ```
      - Skip to the first incomplete phase

   c. **If no workflow exists:**
      - Create new workflow file from `templates/core/workflow.md`
      - Write to `sdlc-studio/workflows/WF{NNNN}-{story-slug}.md`
      - Assign next available workflow ID
      - **STOP if file creation fails** - do not proceed without workflow state

   d. **If `--from-phase N` specified:**
      - Override resume point to phase N
      - Update workflow state to reflect manual override

2. **Validate Prerequisites (STOP if any fail)**

   a. **Check story exists and has correct status:**
      - Story file must exist in `sdlc-studio/stories/`
      - Status must be Planned or In Progress
      - If status is Ready/Draft: **STOP** - plan not created yet

   b. **Check plan file exists (MANDATORY):**
      - Search for `sdlc-studio/plans/PL*-{story-slug}.md`
      - **If plan does NOT exist, STOP immediately:**
        ```
        ## Cannot Proceed - No Plan Found

        **Story:** US0024 - Action Queue API
        **Status:** Ready

        A plan must be created before implementation can begin.
        The plan defines implementation tasks, approach, and provides
        an audit trail for the work.

        ### To Create a Plan
        Run: /sdlc-studio story plan --story US0024

        This will:
        1. Create the implementation plan (PL0024)
        2. Create the test specification (TS0024)
        3. Update story status to Planned
        4. Present artifacts for review

        Then run: /sdlc-studio story implement --story US0024
        ```

   c. **Check test spec file exists:**
      - Search for `sdlc-studio/test-specs/TS*-{story-slug}.md`
      - If missing but plan exists: warn but allow to continue
        (test spec can be created during workflow)

   d. **Check dependencies:**
      - Dependencies met (or acknowledged if resuming)
      - No unresolved blocking errors in workflow state

3. **Apply Approach Override**
   - If `--tdd` flag: use TDD phase order
   - If `--no-tdd` flag: use Test-After phase order
   - Otherwise: use approach from plan's "Recommended Approach" section

4. **Execute Phases (with Progress Tracking)**

   For each phase (starting from resume point):

   a. **Update workflow state BEFORE starting phase:**
      - Set phase status to "In Progress"
      - Record start timestamp
      - Write workflow file to disk

   b. **Execute phase command:**
      | Phase | Command | Artifacts |
      |-------|---------|-----------|
      | 1 | `code plan --story US000X` | Plan file |
      | 2 | `test-spec --story US000X` | Test spec file |
      | 3 | `code implement --plan PL000X` | Source files |
      | 4 | `test-automation --spec TS000X` | Test files |
      | 5 | `code test --story US000X` | Test results |
      | 6 | `code verify --story US000X` | AC verification |
      | 7 | `code check` | Lint results |
      | 8 | Review | Final status |

   c. **Update plan checkboxes (MANDATORY for Phase 3):**
      During implementation (Phase 3), as each task completes:
      - Read the plan file
      - Find the task in "Implementation Tasks" table
      - Change `[ ]` to `[x]`
      - Write the plan file
      - Update workflow state with task completion

      Example plan update:
      ```markdown
      | 1 | Add isPaused prop to StatusLED | `StatusLED.tsx` | - | [x] |
      | 2 | Add paused state styling | `StatusLED.tsx` | 1 | [x] |
      | 3 | Import Wrench icon | `ServerCard.tsx` | - | [ ] |  ← next task
      ```

   d. **Update workflow state AFTER phase completes:**
      - Set phase status to "Done" (success) or "Paused" (failure)
      - Record completion timestamp
      - Record any notes or errors
      - Update "Current Phase" pointer
      - Add session log entry
      - Write workflow file to disk

5. **Handle Phase Errors (with State Preservation)**

   When a phase fails:

   a. **Update workflow state immediately:**
      - Set phase status to "Paused"
      - Record error message in "Errors & Pauses" section
      - Set workflow status to "Paused"
      - Write workflow file to disk

   b. **Report error with resume path:**
      ```
      ## Workflow Paused

      **Story:** US0024 - Action Queue API
      **Phase:** 5. Test
      **Error:** 2 tests failed

      ### Failed Tests
      - test_action_queue_empty: Expected 200, got 500
      - test_action_invalid_id: AssertionError

      ### State Saved
      Workflow state saved to: sdlc-studio/workflows/WF0024-action-queue-api.md
      Plan progress saved: 6/8 tasks complete

      ### To Resume
      1. Fix the failing tests or implementation
      2. Run: /sdlc-studio story implement --story US0024
         (Will automatically resume from Phase 5)

      Or to skip to next phase:
         /sdlc-studio story implement --story US0024 --from-phase 6
      ```

6. **Complete Workflow (with Full State Update)**

   When all phases pass:

   a. **Update all artifact statuses (Status Cascade):**
      This is the most critical step. Execute the **Story Completion Cascade** for the story being completed.

      > **Canonical checklist:** `reference-outputs.md` → [Story Completion Cascade](#story-completion-cascade)

      Follow all six steps: update plan, update test spec, update workflow, recalculate index counts, check epic status, and document reason (for non-Done terminals). The story itself should be updated to Done (or the appropriate terminal status if the workflow was terminated early).

      > **Why this is critical:** Without this cascade, plan and test spec files accumulate stale statuses (Draft/Ready/In Progress) while the story shows Done. This creates misleading dashboard output. Every story terminal status MUST cascade to all linked artifacts.

   b. **Verify plan task completion:**
      - Read plan file
      - Check all tasks have `[x]`
      - If any unchecked, report warning

   c. **Update workflow completion section:**
      - Record completion date
      - Calculate total duration
      - List all artifacts created

   d. **Report completion with audit trail:**
      ```
      ## Workflow Complete

      **Story:** US0024 - Action Queue API
      **Workflow:** WF0024
      **Duration:** 45 minutes (across 2 sessions)
      **Approach:** TDD

      ### Phase Summary
      | Phase | Status | Completed |
      |-------|--------|-----------|
      | 1. Plan | Done | 2026-01-27 10:15 |
      | 2. Test Spec | Done | 2026-01-27 10:22 |
      | 3. Implement | Done | 2026-01-27 10:37 |
      | 4. Tests | Done | 2026-01-27 10:45 |
      | 5. Test | Done | 2026-01-28 09:12 |
      | 6. Verify | Done | 2026-01-28 09:14 |
      | 7. Check | Done | 2026-01-28 09:15 |
      | 8. Review | Done | 2026-01-28 09:16 |

      ### Plan Tasks: 8/8 Complete
      All implementation tasks checked off in plan file.

      ### Artifacts
      - Workflow: sdlc-studio/workflows/WF0024-action-queue-api.md
      - Plan: sdlc-studio/plans/PL0024-action-queue-api.md
      - Test Spec: sdlc-studio/test-specs/TS0024-action-queue-api.md
      - Tests: tests/test_action_queue_api.py
      - Source: src/api/action_queue.py
      ```

---

## Workflow Error Handling {#workflow-error-handling}

### Phase-Specific Errors {#phase-specific-errors}

| Phase | Error | Cause | Resolution |
|-------|-------|-------|------------|
| 1. Plan | Story not Ready | Missing Ready criteria | Complete story preparation |
| 1. Plan | Dependency not Done | Blocking story incomplete | Complete dependency first |
| 2. Test Spec | AC coverage gap | AC not testable | Clarify AC in story |
| 3. Tests | Generation fails | Test framework issue | Check framework config |
| 4. Implement | Syntax error | Code bug | Fix code |
| 5. Test | Tests fail | Implementation bug | Fix implementation |
| 6. Verify | AC not met | Missing functionality | Address verification issues |
| 7. Check | Lint errors | Style violations | Run auto-fix or manual fix |
| 8. Review | Status issues | Gaps in coverage/quality | Address before marking done |

### Recovery Strategies {#story-recovery-strategies}

**Option 1: Fix and Resume**
```bash
# Fix the issue manually
# Then resume from failed phase
/sdlc-studio story implement --story US0024 --from-phase 5
```

**Option 2: Skip Phase**
```bash
# Manual phase execution
/sdlc-studio code test --story US0024
# Then resume
/sdlc-studio story implement --story US0024 --from-phase 6
```

**Option 3: Restart Workflow**
```bash
# Delete workflow file and start fresh
rm sdlc-studio/workflows/WF0024-action-queue-api.md
/sdlc-studio story implement --story US0024
```

---

# See Also

- `reference-epic.md` - Epic workflows
- `reference-epic.md#flag-agentic` - `--agentic` flag for concurrent story execution
- `reference-persona.md` - Persona workflows
- `reference-consult.md` - Persona consultation for story validation
- `reference-bug.md` - Bug tracking workflows
- `reference-decisions.md` - Ready criteria, dependency detection, decision guidance
- `reference-code.md` - Code plan, implement, review workflows (includes workflow orchestration)
- `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` - Test workflows
- `reference-philosophy.md` - Create vs Generate philosophy

---

## Navigation {#navigation}

**Prerequisites (load these first):**
- `reference-epic.md` - Epic workflows (epics must exist before generating stories)

**Related workflows:**
- `reference-code.md` - Code planning (downstream - stories feed into code plans)
- `reference-persona.md` - Personas (referenced in every story)

**Cross-cutting concerns:**
- `reference-decisions.md` - Decision guidance and Ready criteria
- `reference-outputs.md#output-formats` - File formats and status values

**Deep dives (optional):**
- `reference-test-spec.md` - Test workflows (stories link to test specs)
- `reference-bug.md` - Bug tracking (bugs link to stories)
- `reference-philosophy.md` - Create vs Generate philosophy
