# SDLC Studio Reference - Story

Detailed workflows for User Story generation, quality enforcement, and management.

<!-- Load when: generating or managing Stories -->

---

# Story Workflows

## /sdlc-studio story - Step by Step

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
   - Use `templates/story-template.md`
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

---

## /sdlc-studio story review - Step by Step

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

4. **Update Related Files**
   - Update _index.md with status counts
   - Check if Epic should be reviewed

5. **Report**
   - Stories completed
   - Stories in progress
   - Stories blocked
   - Regressions

---

## /sdlc-studio story generate - Step by Step (Specification Extraction)

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
   - Use `templates/story-template.md`
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

## Quality Checklist

### API Stories

| Requirement | Minimum | Check |
|-------------|---------|-------|
| Edge cases | 8+ with specific inputs/outputs | `grep -c "\| Scenario" story.md` |
| Test scenarios | 10+ | `grep -c "- \[ \]" story.md` |
| Request/response shapes | Exact JSON documented | AC includes full schema |
| Error codes | All codes with messages | Edge case table complete |
| Validation rules | Extracted from code | Not assumed or guessed |

### All Stories

- [ ] No ambiguous language ("handles errors", "returns data", "works correctly")
- [ ] All Open Questions have target resolution dates
- [ ] Critical Open Questions resolved before Ready status
- [ ] Given/When/Then uses concrete values, not placeholders
- [ ] Persona referenced with specific context (not just name)

## Blocking Conditions

**Do NOT mark Ready if:**

| Condition | Why It Blocks |
|-----------|---------------|
| Critical Open Question unresolved | Specification incomplete |
| Edge case count below 8 (API stories) | Test coverage will have gaps |
| API contracts use vague language | Implementer will make assumptions |
| "TBD" still in acceptance criteria | Story is not actually ready |
| No error scenarios documented | Happy-path-only specification |

## Ambiguous Language Detection

> **Source of truth:** `reference-decisions.md` → Ambiguous Language Detection

These phrases indicate specification gaps. Replace before marking Ready.

## Quality Metrics

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

Detailed guidance for completing each section of the User Story template.

---

## User Story Statement

### Format
**As a** {persona name from personas.md}
**I want** {specific capability or action}
**So that** {concrete benefit or outcome}

### Good Examples
- As a **new user**, I want **to reset my password via email** so that **I can regain access without contacting support**.
- As a **team lead**, I want **to see my team's activity summary** so that **I can identify blockers in our standup**.

### Bad Examples
- As a user, I want a button... (which user? button for what?)
- As a developer, I want clean code... (not user-facing value)
- As a user, I want the system to be fast... (not specific action)

---

## Context

### Persona Reference
- Link to full persona in personas.md
- Include relevant summary (goals, pain points)
- Helps developers understand who they're building for

### Background
- Why does this story exist?
- What led to this need?
- Business context not obvious from Epic

---

## Acceptance Criteria

### Given/When/Then Format
- **Given**: precondition or context
- **When**: action taken
- **Then**: observable outcome

### Guidelines
- 3-5 criteria per story
- Each criterion independently testable
- Cover happy path AND key edge cases
- Avoid implementation details

### Good Example
```
### AC1: Successful password reset
- **Given** user has a registered email address
- **When** they submit the password reset form
- **Then** they receive a reset link within 5 minutes
```

### Bad Example
```
### AC1: Works correctly
- **Given** user is logged in
- **When** they use the feature
- **Then** it works
```

---

## Scope

### In Scope
- What this specific story delivers
- Boundaries prevent scope creep
- Be precise (e.g., "Email reset only, not SMS")

### Out of Scope
- Related functionality NOT in this story
- Explicitly state to prevent misunderstandings
- Reference other stories if covered elsewhere

---

## UI/UX Requirements

### When to Include
- User-facing functionality
- Visual or interaction requirements
- Accessibility considerations

### What to Include
- Wireframe or design references
- Design system components to use
- Behavioural specifications (animations, transitions)
- Responsive requirements

---

## Technical Notes

### Purpose
- Guide developers without prescribing solution
- Share relevant context
- Prevent known pitfalls

### API Contracts
- Expected request/response shapes
- Error codes and messages
- Authentication requirements

### Data Requirements
- Schema changes needed
- Data sources
- Validation rules

---

## Edge Cases & Error Handling

### What to Include
- Unusual but valid scenarios
- Error conditions
- Recovery behaviours

### Format
| Scenario | Expected Behaviour |
|----------|-------------------|
| User submits expired reset link | Show "Link expired" with option to request new |
| Network timeout during submit | Show retry option, preserve form data |

---

## Test Scenarios

### Purpose
- Key scenarios for QA
- NOT exhaustive test cases
- Helps estimate test effort

### Guidelines
- Focus on user journeys
- Include happy path and key edge cases
- Checkbox format for tracking

---

## Definition of Done

### Standard Reference
- Link to project-level DoD
- Don't repeat standard items

### Story-Specific Additions
- Additional criteria for THIS story
- Security review needed?
- Performance benchmark required?
- Specific documentation?

---

## Estimation

### Story Points
- Filled in during team refinement
- Initially `{{TBD}}` from generation
- Fibonacci sequence (1, 2, 3, 5, 8, 13)

### Complexity
- Low: familiar patterns, no unknowns
- Medium: some new elements, manageable risk
- High: significant unknowns, new technology

---


# Workflow Commands

Automated workflows for complete story implementation.

## /sdlc-studio story plan - Step by Step

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

4. **Create Implementation Plan**
   - Run `code plan --story US000X` internally
   - Verify plan creates successfully
   - Store plan ID for workflow tracking

5. **Create Test Specification**
   - Run `test-spec --story US000X` internally
   - Verify spec creates successfully
   - Store spec ID for workflow tracking

6. **Generate Preview**
   Output workflow plan to console:
   ```
   ## Story Workflow Plan: US0024

   **Story:** Action Queue API Endpoint
   **Status:** Ready
   **Dependencies:** US0023 (Done)

   ### Approach: TDD
   Reason: API story with 8 edge cases, clear Given/When/Then AC

   ### Execution Phases

   | Phase | Command | Artifacts |
   |-------|---------|-----------|
   | 1. Plan | code plan | PL0024-action-queue-api.md |
   | 2. Test Spec | test-spec | TS0024-action-queue-api.md |
   | 3. Tests | test-automation | tests/test_action_queue_api.py |
   | 4. Implement | code implement | src/api/action_queue.py |
   | 5. Test | code test | Run tests |
   | 6. Verify | code verify | Verify against AC |
   | 7. Check | code check | Quality gates |

   Ready to execute? Run: /sdlc-studio story implement --story US0024
   ```

---

## /sdlc-studio story implement - Step by Step

1. **Load or Create Workflow State**
   - Check for existing workflow file in sdlc-studio/workflows/
   - If exists, load state and determine resume point
   - If not exists, create from `templates/workflow-template.md`
   - Assign next workflow ID: WF{NNNN}

2. **Validate Prerequisites**
   - Story exists and is Ready status
   - Dependencies met (or `--from-phase` used to skip validation)
   - No blocking errors in previous phases (if resuming)

3. **Apply Approach Override**
   - If `--tdd` flag: use TDD phase order
   - If `--no-tdd` flag: use Test-After phase order
   - Otherwise: use approach from story plan

4. **Execute Phases**
   For each phase (1-7):

   a. **Update workflow state**: Phase → In Progress

   b. **Execute phase command**:
      | Phase | Command |
      |-------|---------|
      | 1 | `code plan --story US000X` |
      | 2 | `test-spec --story US000X` |
      | 3 | `test-automation --spec TS000X` |
      | 4 | `code implement --plan PL000X` |
      | 5 | `code test --story US000X` |
      | 6 | `code verify --story US000X` |
      | 7 | `code check` |

   c. **Check result**:
      - On success: Update phase → Done, continue
      - On failure: Update phase → Paused, record error, stop

5. **Handle Phase Errors**
   When a phase fails:
   - Record error in workflow file
   - Update workflow status to Paused
   - Report error and resume instructions:
     ```
     ## Workflow Paused

     **Story:** US0024 - Action Queue API
     **Phase:** 5. Verify
     **Error:** 2 tests failed

     ### Failed Tests
     - test_action_queue_empty: Expected 200, got 500
     - test_action_invalid_id: AssertionError

     ### To Resume
     1. Fix the failing tests or implementation
     2. Run: /sdlc-studio story implement --story US0024 --from-phase 5
     ```

6. **Complete Workflow**
   When all phases pass:
   - Update workflow status to Done
   - Update story status to Done (or Review if `code verify` had issues)
   - Report completion:
     ```
     ## Workflow Complete

     **Story:** US0024 - Action Queue API
     **Duration:** 45 minutes
     **Approach:** TDD

     ### Summary
     | Phase | Status | Duration |
     |-------|--------|----------|
     | 1. Plan | Done | 5m |
     | 2. Test Spec | Done | 7m |
     | 3. Tests | Done | 12m |
     | 4. Implement | Done | 15m |
     | 5. Verify | Done | 2m |
     | 6. Review | Done | 3m |
     | 7. Check | Done | 1m |

     ### Artifacts Created
     - sdlc-studio/plans/PL0024-action-queue-api.md
     - sdlc-studio/test-specs/TS0024-action-queue-api.md
     - tests/test_action_queue_api.py
     - src/api/action_queue.py
     ```

---

## Workflow Error Handling

### Phase-Specific Errors

| Phase | Error | Cause | Resolution |
|-------|-------|-------|------------|
| 1. Plan | Story not Ready | Missing Ready criteria | Complete story preparation |
| 1. Plan | Dependency not Done | Blocking story incomplete | Complete dependency first |
| 2. Test Spec | AC coverage gap | AC not testable | Clarify AC in story |
| 3. Tests | Generation fails | Test framework issue | Check framework config |
| 4. Implement | Syntax error | Code bug | Fix code |
| 5. Verify | Tests fail | Implementation bug | Fix implementation |
| 6. Review | Issues found | AC not met | Address review issues |
| 7. Check | Lint errors | Style violations | Run auto-fix or manual fix |

### Recovery Strategies

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
- `reference-bug.md` - Bug tracking workflows
- `reference-decisions.md` - Ready criteria, dependency detection, decision guidance
- `reference-code.md` - Code plan, implement, review workflows (includes workflow orchestration)
- `reference-testing.md` - Test Strategy, Spec, Automation workflows
- `reference-philosophy.md` - Create vs Generate philosophy
