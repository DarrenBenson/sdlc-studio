# SDLC Studio Reference - Epic

Detailed workflows for Epic generation and management.

<!-- Load when: generating or managing Epics -->

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
   - Use `templates/epic-template.md`
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

## /sdlc-studio epic review - Step by Step {#epic-review-workflow}

1. **Load Epics**
   - Read all from sdlc-studio/epics/
   - Parse acceptance criteria and story links

2. **Check Story Status**
   For each Epic:
   - Read linked stories
   - Calculate completion percentage
   - If any In Progress → Epic In Progress
   - **"Done" rules:**
     - If epic has stories AND all stories Done → suggest "Done" (user confirms)
     - If epic has NO stories → cannot auto-mark "Done"
     - Prompt: "All stories complete. Mark epic as Done? [y/N]"

     > **Principle:** `reference-decisions.md` → Status Transition Rules

3. **Analyse Implementation**
   Use Task tool with Explore agent:
   ```
   For epic [Title], check implementation:
   1. Code implementing acceptance criteria
   2. Test coverage for epic features
   3. Related documentation
   Assess: What percentage complete?
   ```

4. **Update Files**
   - Update Status field
   - Update acceptance criteria checkboxes
   - Add revision history entry
   - Update _index.md

5. **Report**
   - Epics completed
   - Epics in progress
   - Epics blocked or regressed

---

# Epic Section Reference

Detailed guidance for completing each section of the Epic template.

---

## Summary {#summary}

### What to Include {#summary-what-to-include}
- 2-3 sentences describing what this Epic delivers
- Written for someone unfamiliar with the project
- Focus on user value, not technical implementation

### What to Avoid {#summary-what-to-avoid}
- Technical jargon without explanation
- Implementation details (save for stories)
- Vague statements like "improve the system"

---

## Business Context {#business-context}

### Problem Statement {#problem-statement}
- Extract from PRD's Problem Statement
- Focus on the specific aspect this Epic addresses
- Reference PRD section for traceability

### Value Proposition {#value-proposition}
- What happens if we DO this?
- What happens if we DON'T?
- Quantify where possible

### Success Metrics {#success-metrics}
- Must be measurable
- Include baseline (current state) even if "N/A"
- Specify how measurement will occur
- Examples: completion rate, time reduction, error rate

---

## Scope {#scope}

### In Scope {#in-scope}
- Be specific about what's included
- List features, not implementation details
- Helps prevent scope creep

### Out of Scope {#out-of-scope}
- Explicitly state exclusions
- Include brief rationale (helps prevent arguments later)
- Can reference "future Epic" if planned

### Affected Personas {#affected-personas}
- Link to personas.md
- Describe HOW this Epic affects each persona
- Helps prioritise and validate stories

---

## Acceptance Criteria (Epic Level) {#acceptance-criteria}

### Format {#ac-format}
- High-level, observable outcomes
- Use checkboxes for tracking
- NOT detailed Given/When/Then (save for stories)

### Good Examples {#ac-good-examples}
- [ ] Users can complete registration without assistance
- [ ] Dashboard loads within 2 seconds
- [ ] All data is encrypted at rest

### Bad Examples {#ac-bad-examples}
- [ ] Code is written (too vague)
- [ ] Tests pass (that's DoD, not AC)
- [ ] Given user clicks button, When... (too detailed for Epic)

---

## Dependencies {#dependencies}

### Blocked By {#blocked-by}
- Other Epics that must complete first
- External systems or APIs
- Data migrations or infrastructure
- Include impact notes (what happens if delayed)

### Blocking {#blocking}
- What's waiting on this Epic
- Helps prioritise and communicate urgency
- Include consequence of delay

---

## Risks & Assumptions {#risks-and-assumptions}

### Assumptions {#assumptions}
- What are we taking for granted?
- Each should be validateable
- If assumption proves wrong, impact should be assessed

### Risks {#risks}
- Technical risks (new technology, integration)
- Business risks (user adoption, market timing)
- Resource risks (availability, skills)
- Include likelihood/impact for prioritisation
- Must have mitigation strategy

---

## Technical Considerations {#technical-considerations}

### Architecture Impact {#architecture-impact}
- Does this require new services?
- Significant refactoring needed?
- Infrastructure changes?
- Keep high-level (details in stories)

### Integration Points {#integration-points}
- External APIs and services
- Internal system boundaries
- Authentication/authorisation touchpoints

### Data Considerations {#data-considerations}
- New data models
- Migrations required
- Data dependencies from other systems

---

## Sizing & Effort {#sizing-and-effort}

### Story Points {#story-points}
- Relative sizing (1, 2, 3, 5, 8, 13, 21)
- Based on complexity, not time
- Compare to reference Epics

### Story Count {#story-count}
- Estimate range (e.g., "8-12 stories")
- Helps sprint planning
- Refine after story generation

### Complexity Factors {#complexity-factors}
- What makes this harder than it looks?
- New technology, integrations, unknowns
- Helps justify sizing

---

## Story Breakdown {#story-breakdown}

### Before Story Generation {#before-story-generation}
- Provisional titles only
- Use `- [ ] US{{TBD}}: {Title}`

### After Story Generation {#after-story-generation}
- Updated automatically by `/sdlc-studio story`
- Links to actual story files
- Status tracked via story files

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
- `reference-testing.md` - Test Strategy, Spec, Automation workflows
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
