# SDLC Studio Reference - Epic

Detailed workflows for Epic generation and management.

<!-- Load when: generating or managing Epics -->

## Reading Guide

| Section | When to Read |
|---------|--------------|
| Epic Workflows | When generating epics from PRD |
| Perspective-Based Generation | When using `--perspective` flag |
| Epic Review Workflow | When reviewing epic status (cascade or quick) |
| Workflow Commands | When using `epic plan` or `epic implement` |
| Section Reference | See `reference-epic-sections.md` for template guidance |

---

# Epic Workflows

## /sdlc-studio epic - Step by Step {#epic-workflow}

1. **Check Prerequisites**
   - Verify PRD exists at sdlc-studio/prd.md
   - Create sdlc-studio/epics/ if needed
   - Scan for existing epics to determine next ID

2. **Parse PRD**
   - Extract Feature Inventory section
   - Extract Problem Statement for context
   - Note dependencies between features

3. **Group Features into Epics**
   Heuristics:
   - Features sharing user type → same Epic
   - Features with shared dependencies → same Epic
   - Features forming complete user journey → same Epic
   - Maximum 5-8 features per Epic

4. **Generate Epic Files**
   For each Epic:
   - Assign ID: EP{NNNN}
   - Create slug (kebab-case, max 50 chars)
   - Use `templates/core/epic.md`
   - Fill all sections from PRD data
   - Estimate story points
   - **Status Rules:**
     - New epics → "Draft"
     - After review/approval → "Ready" or "Approved"

     > **Source of truth:** `reference-decisions.md` → Status Transition Rules

5. **Write Files**
   - Write `sdlc-studio/epics/EP{NNNN}-{slug}.md`
   - Create/update `sdlc-studio/epics/_index.md`

6. **Report**
   - Number of Epics created
   - List with IDs and titles
   - Orphan features (if any)

---

## Perspective-Based Generation {#perspective-based-generation}

Use `--perspective` to generate epics with specific focus areas aligned to document types. This creates a consistent mental model:
- **Product perspective** → PRD-style breakdown (features, user value)
- **Engineering perspective** → TRD-style breakdown (technical architecture)
- **Test perspective** → TSD-style breakdown (quality strategy)

### Engineering Perspective (--perspective engineering) {#perspective-engineering}

Aligns with TRD - generates epics emphasising technical structure.

**Additional sections per epic:**

| Section | Content |
|---------|---------|
| Components | Component boundaries and ownership |
| API Contracts | Endpoints, methods, schemas |
| Data Models | New/modified entities and relationships |
| Infrastructure | Infrastructure requirements |
| Tech Dependencies | Libraries, services, versions |
| Performance | Performance considerations and targets |
| Security | Security implications and mitigations |

**Story emphasis:** Technical implementation details, API specifications, data schemas.

**Example output:**
```markdown
### Engineering View (TRD-aligned)

**Components:**
- UserAuthService: Handles authentication flows (Owner: Backend Team)
- SessionManager: Manages session lifecycle (Owner: Backend Team)
- AuthMiddleware: Request authentication (Owner: Platform Team)

**API Contracts:**
- `POST /api/v1/auth/login`: Authenticate user credentials
- `POST /api/v1/auth/refresh`: Refresh access token
- `DELETE /api/v1/auth/logout`: Invalidate session

**Data Models:**
- User: id, email, password_hash, created_at, last_login
- Session: id, user_id, token_hash, expires_at, ip_address

**Technical Dependencies:**
- bcrypt (14.0): Password hashing
- jsonwebtoken (9.0): JWT creation/verification
- redis (4.6): Session storage
```

### Product Perspective (--perspective product) {#perspective-product}

Aligns with PRD - generates epics emphasising business value.

**Additional sections per epic:**

| Section | Content |
|---------|---------|
| User Value | Clear statement of user benefit |
| Success Metrics | Measurable outcomes with baselines and targets |
| Priority Rationale | Why this order? Business justification |
| Stakeholder Impact | Who is affected and how |
| Release Considerations | Timing, dependencies, rollout strategy |
| Business Risk | Risk if delayed or not delivered |

**Story emphasis:** User benefits, acceptance criteria from user perspective.

**Example output:**
```markdown
### Product View (PRD-aligned)

**User Value:** Users can securely access their accounts with minimal friction, reducing support tickets by 40%.

**Success Metrics:**
| Metric | Baseline | Target |
|--------|----------|--------|
| Login success rate | 87% | 95% |
| Password reset requests | 50/day | 20/day |
| Support tickets (auth) | 25/week | 10/week |

**Priority Rationale:** Authentication is foundational - blocks user profile, settings, and personalisation features. Delivery in Q1 unblocks Q2 roadmap.

**Stakeholder Impact:**
| Stakeholder | Impact | Mitigation |
|-------------|--------|------------|
| End Users | New login flow | Gradual rollout, clear guidance |
| Support | Training needed | Documentation, FAQs |
| Marketing | Can promote security | Press release coordination |
```

### Test Perspective (--perspective test) {#perspective-test}

Aligns with TSD - generates epics emphasising quality assurance.

**Additional sections per epic:**

| Section | Content |
|---------|---------|
| Test Types Required | Unit, integration, E2E with coverage targets |
| Risk-Based Priorities | What to test first based on risk |
| Test Data Requirements | What data needed for testing |
| Automation Candidates | What can/should be automated |
| Manual Testing Needs | What requires human verification |
| Performance Scenarios | Load, stress, endurance tests |

**Story emphasis:** Test scenarios, edge cases, failure modes.

**Example output:**
```markdown
### Test View (TSD-aligned)

**Test Types Required:**
| Type | Coverage Target | Automation |
|------|-----------------|------------|
| Unit | 90% | Fully automated |
| Integration | 80% | Fully automated |
| E2E | Critical paths | Automated |
| Security | OWASP Top 10 | Automated scans + manual |

**Risk-Based Priorities:**
1. Session hijacking prevention - High risk - Security scan + penetration test
2. Password brute force - High risk - Rate limiting tests
3. Token expiration - Medium risk - Automated timing tests
4. Concurrent logins - Medium risk - Load testing

**Test Data Requirements:**
- users_valid: 100 valid user accounts with various states
- users_locked: 20 accounts in locked state
- tokens_expired: Pre-generated expired tokens for testing

**Automation Candidates:**
- Login flow happy path (E2E)
- Token refresh cycle (Integration)
- Password validation rules (Unit)
- Rate limiting behaviour (Integration)
```

---

## /sdlc-studio epic review - Step by Step {#epic-review-workflow}

Epic review now **cascades by default** - it reviews the epic and all changed stories/code. Use `--quick` for epic-only review.

### Command Syntax

```bash
/sdlc-studio epic review              # Cascade review (default) - epic + changed stories
/sdlc-studio epic review --quick      # Quick review - epic only, skip stories
/sdlc-studio epic review --resume     # Resume from last pause point
/sdlc-studio epic review --epic EP0001  # Target specific epic
```

| Flag | Description |
|------|-------------|
| `--quick` | Skip cascade, review only the epic |
| `--resume` | Resume from where review paused |
| `--epic EP0001` | Target specific epic |

### Cascade Workflow (Default) {#cascade-workflow}

```text
1. Build Review Queue
   - Load target epic
   - For each linked story:
     - Check: story spec changed since review?
     - Check: story code changed since review?
   - Add changed items to queue
   - Prioritise: failing tests > spec changes > code changes

2. Execute Reviews
   For each queue item:
   - Story spec: Check AC against implementation
   - Story code: Run code review patterns
   - Store findings in RV{NNNN} file
   - Update .local/review-state.json timestamps

3. Aggregate Epic Review
   - Compile story findings
   - Check epic-level AC
   - Generate summary

4. Report
   - Display findings by severity
   - List actionable items
   - Show what was reviewed vs skipped
```

### Step-by-Step (Cascade Mode)

1. **Load Epic and Build Queue**
   - Read target epic from sdlc-studio/epics/
   - Parse acceptance criteria and story links
   - Load `.local/review-state.json` for modification tracking
   - Build review queue:
     ```text
     For each linked story:
       if needs_re_review(story_spec): add story_spec to queue
       if code_changed_since_review(story): add story_code to queue
     ```
   - Save queue to `.local/review-queue.json` for resume capability

2. **Execute Story Reviews**
   For each item in queue:
   - **Story spec review:**
     - Check AC against implementation
     - Verify edge cases handled
     - Check for regressions
   - **Story code review:**
     - Run code quality checks
     - Check for pattern violations
     - Verify test coverage
   - Store findings in `sdlc-studio/reviews/RV{NNNN}-{story-id}-review.md`
   - Update `.local/review-state.json` with review timestamp

3. **Check Epic-Level Status**
   - Read linked stories
   - Calculate completion percentage
   - If any In Progress → Epic In Progress
   - **"Done" rules:**
     - If epic has stories AND all stories Done → suggest "Done" (user confirms)
     - If epic has NO stories → cannot auto-mark "Done"
     - Prompt: "All stories complete. Mark epic as Done? [y/N]"

     > **Principle:** `reference-decisions.md` → Status Transition Rules

4. **Analyse Implementation**
   Use Task tool with Explore agent:
   ```
   For epic [Title], check implementation:
   1. Code implementing acceptance criteria
   2. Test coverage for epic features
   3. Related documentation
   Assess: What percentage complete?
   ```

5. **Update Files**
   - Update epic Status field
   - Update acceptance criteria checkboxes
   - Add revision history entry
   - Update _index.md
   - Store epic findings in `sdlc-studio/reviews/RV{NNNN}-{epic-id}-review.md`

6. **Report**
   ```text
   ## Epic Review: EP0001 - User Authentication

   ### Cascade Summary
   | Type | Reviewed | Skipped | Findings |
   |------|----------|---------|----------|
   | Story specs | 3 | 2 (unchanged) | 5 |
   | Story code | 2 | 3 (unchanged) | 3 |
   | Epic | 1 | 0 | 2 |

   ### Findings by Severity
   | Severity | Count |
   |----------|-------|
   | Critical | 0 |
   | Important | 4 |
   | Suggestions | 6 |

   ### Stories Reviewed
   - US0001: 2 important issues
   - US0003: 1 important issue, 2 suggestions
   - US0005: 1 suggestion

   ### Stories Skipped (unchanged since last review)
   - US0002: Reviewed 2026-01-25
   - US0004: Reviewed 2026-01-26

   ### Next Steps
   - [ ] Address important issues in US0001
   - [ ] Consider suggestions for US0003
   ```

### Quick Mode (--quick) {#quick-mode}

Skips story cascade, reviews only epic-level concerns:

1. **Load Epic**
   - Read from sdlc-studio/epics/
   - Parse acceptance criteria

2. **Check Story Status**
   - Read linked stories
   - Calculate completion only (no deep review)

3. **Update Epic**
   - Update Status field
   - Update _index.md

4. **Report**
   - Epic status
   - Story completion summary
   - No detailed findings

### Resume Mode (--resume) {#resume-mode}

Continues from last pause point using `.local/review-queue.json`:

1. **Load Queue State**
   - Read `.local/review-queue.json`
   - Find `current_index`
   - Verify queue is still valid (no new changes)

2. **Continue Execution**
   - Resume from paused item
   - Complete remaining queue items

3. **Cleanup**
   - Remove `.local/review-queue.json` on completion
   - Update `.local/review-state.json`

### Review Queue Persistence {#review-queue}

**File:** `sdlc-studio/.local/review-queue.json`

Enables pause/resume if review is interrupted:

```json
{
  "id": "RQ0001",
  "epic": "EP0001",
  "created": "2026-01-27T10:00:00Z",
  "status": "in_progress",
  "queue": [
    { "type": "story_spec", "id": "US0001", "status": "done" },
    { "type": "story_code", "id": "US0001", "status": "in_progress" },
    { "type": "story_spec", "id": "US0002", "status": "pending" }
  ],
  "current_index": 1
}
```

### Review State Tracking {#review-state-tracking}

**File:** `sdlc-studio/.local/review-state.json`

Tracks when each artifact was last reviewed. See `reference-outputs.md#review-state` for schema details.

**Modified-since detection:**

```text
needs_re_review(artifact):
  1. Load entry from review-state.json
  2. If no entry OR no last_reviewed: return TRUE
  3. Get last_modified via git log or file mtime
  4. If last_modified > last_reviewed: return TRUE
  5. return FALSE

code_changed_since_review(story):
  1. Get code_files list from story entry
  2. For each file: check git log timestamp
  3. If any file_modified > story.last_reviewed: return TRUE
  4. return FALSE
```

---

# Epic Section Reference

> **Section-by-section guidance:** See `reference-epic-sections.md` for detailed guidance on completing each section of the epic template (Summary, Business Context, Scope, AC, Dependencies, Risks, Technical Considerations, Sizing, Story Breakdown).

---

# Workflow Commands

Automated workflows for implementing all stories in an epic.

## /sdlc-studio epic plan - Step by Step {#epic-plan-workflow}

1. **Load Epic**
   - Read epic file from sdlc-studio/epics/
   - Verify epic exists and has stories

2. **List Stories**
   - Read all stories linked to epic
   - Filter to stories needing implementation:
     - Status: Ready (include)
     - Status: Done (exclude)
     - Status: Draft (warn - not ready)

3. **Analyse Dependencies**
   - Build dependency graph from story Dependencies sections
   - Detect cross-story dependencies:
     - Schema dependencies
     - API dependencies
     - Service dependencies
   - Check for circular dependencies (abort if found)

4. **Determine Execution Order**
   Use topological sort:
   ```
   1. Find stories with no dependencies
   2. Process those first
   3. Unlock dependent stories as each completes
   4. Repeat until all stories processed
   ```

5. **Determine Approach Per Story**
   For each story, apply TDD decision tree:
   - API story with >5 edge cases → TDD
   - UI-heavy story → Test-After
   - Clear AC with complex rules → TDD
   - Exploratory implementation → Test-After

6. **Generate Preview**
   Output epic workflow plan:
   ```
   ## Epic Workflow Plan: EP0004

   **Epic:** Agent Execution Engine
   **Stories:** 8 total (3 Done, 5 Ready)

   ### Execution Order

   | Order | Story | Title | Dependencies | Approach |
   |-------|-------|-------|--------------|----------|
   | 1 | US0023 | Config Schema | None | TDD |
   | 2 | US0024 | Action Queue API | US0023 | TDD |
   | 3 | US0025 | Script Parser | US0023 | TDD |
   | 4 | US0026 | Action Executor | US0024, US0025 | TDD |
   | 5 | US0027 | Agent Runner | US0026 | Test-After |

   ### Summary
   - **Stories to implement:** 5
   - **TDD stories:** 4
   - **Test-After stories:** 1
   - **Estimated phases:** 40 (8 per story)

   ### Dependency Graph
   US0023 --+-- US0024 --+-- US0026 -- US0027
            +-- US0025 --+

   Ready to execute? Run: /sdlc-studio epic implement --epic EP0004
   ```

---

## /sdlc-studio epic implement - Step by Step {#epic-implement-workflow}

1. **Load or Create Epic Workflow State**
   - Check for existing workflow in sdlc-studio/workflows/
   - If exists, load state and determine resume point
   - If not exists, create from `templates/epic-workflow-template.md`
   - Assign next workflow ID: WF{NNNN}

2. **Validate Prerequisites**
   - Epic exists
   - Has stories in Ready status
   - No circular dependencies
   - If `--story` flag, validate that story is in epic

3. **Determine Starting Point**
   - If `--story US000X`: start from that story
   - Otherwise: start from first story in execution order

4. **Process Stories**
   For each story in execution order:

   a. **Check Dependencies**
      - All dependent stories must be Done
      - If not Done, mark story as Blocked and skip

   b. **Execute Story Workflow**
      ```
      /sdlc-studio story implement --story US000X
      ```

   c. **Handle Result**
      - On success: Update story → Done, continue to next
      - On failure: Pause epic workflow, report error

5. **Handle Story Errors**
   When a story workflow fails:
   - Update epic workflow status to Paused
   - Record which story and phase failed
   - Report error and resume instructions:
     ```
     ## Epic Workflow Paused

     **Epic:** EP0004 - Agent Execution Engine
     **Paused At:** US0024 - Action Queue API
     **Story Phase:** 5. Verify (tests failed)

     ### Story Progress
     | Story | Status | Notes |
     |-------|--------|-------|
     | US0023 | Done | Completed |
     | US0024 | Paused | Tests failed |
     | US0025 | Pending | |
     | US0026 | Blocked | Waiting for US0024 |
     | US0027 | Blocked | Waiting for US0026 |

     ### To Resume
     1. Fix the issue in US0024
     2. Run: /sdlc-studio epic implement --epic EP0004 --story US0024
     ```

6. **Complete Epic Workflow**
   When all stories complete:
   - Update epic workflow status to Done
   - Update epic status to Done (user confirms)
   - Report completion:
     ```
     ## Epic Workflow Complete

     **Epic:** EP0004 - Agent Execution Engine
     **Duration:** 3 hours 45 minutes
     **Stories:** 5 completed

     ### Summary
     | Story | Status | Duration | Approach |
     |-------|--------|----------|----------|
     | US0023 | Done | 35m | TDD |
     | US0024 | Done | 52m | TDD |
     | US0025 | Done | 41m | TDD |
     | US0026 | Done | 58m | TDD |
     | US0027 | Done | 39m | Test-After |

     Run `/sdlc-studio epic review` to update epic status.
     ```

---

## Workflow Flags {#workflow-flags}

### --story US000X {#flag-story}

Start from specific story (useful for resume):
```bash
/sdlc-studio epic implement --epic EP0004 --story US0024
```

### --skip US000X {#flag-skip}

Skip a problematic story and continue:
```bash
/sdlc-studio epic implement --epic EP0004 --skip US0025
```

---

## Epic Workflow Error Handling {#epic-workflow-error-handling}

### Error Types {#error-types}

| Error | Action |
|-------|--------|
| Story workflow fails | Pause epic at failing story |
| Circular dependency detected | Abort with dependency graph |
| All remaining stories blocked | Pause with blocker info |
| Story not in Ready status | Skip with warning |

### Recovery Strategies {#recovery-strategies}

**Option 1: Fix and Resume**
```bash
# Fix the issue in the failed story
# Then resume from that story
/sdlc-studio epic implement --epic EP0004 --story US0024
```

**Option 2: Skip and Continue**
```bash
# Skip problematic story, continue with others
/sdlc-studio epic implement --epic EP0004 --skip US0024
```

**Option 3: Manual Story Completion**
```bash
# Complete story manually
/sdlc-studio story implement --story US0024 --from-phase 5
# Then resume epic
/sdlc-studio epic implement --epic EP0004 --story US0025
```

---

# See Also

- `reference-story.md` - Story workflows
- `reference-bug.md` - Bug tracking workflows
- `reference-decisions.md` - Ready criteria, decision guidance
- `reference-code.md` - Code plan, implement, review workflows (includes workflow orchestration)
- `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` - Test workflows
- `reference-philosophy.md` - Create vs Generate philosophy

---

## Navigation {#navigation}

**Prerequisites (load these first):**
- `reference-prd.md` - Product Requirements (must exist before generating epics)

**Related workflows:**
- `reference-story.md` - User Stories (downstream - epics decompose into stories)
- `reference-persona.md` - Personas (referenced when scoping epics)

**Cross-cutting concerns:**
- `reference-decisions.md` - Decision guidance and Ready criteria
- `reference-outputs.md#output-formats` - File formats and status values

**Deep dives (optional):**
- `reference-code.md` - Code workflows (epic workflow orchestration)
- `reference-philosophy.md` - Create vs Generate philosophy
