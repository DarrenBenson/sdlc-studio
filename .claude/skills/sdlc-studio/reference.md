# SDLC Studio Reference

Detailed workflows and section guidance for SDLC Studio.

---

# Detailed Workflows

## /sdlc-studio prd create - Step by Step

1. **Gather Project Context**
   Use AskUserQuestion to collect:
   - Project name and one-line description
   - Target users (who will use this?)
   - Problem being solved (what pain point?)
   - Tech stack preferences

2. **Scan Existing Documentation**
   Look for context in:
   - README.md, README files
   - docs/ folder
   - package.json, requirements.txt, pyproject.toml
   - Existing architecture docs

3. **Feature Discovery**
   For each major feature area, ask:
   - Feature name and description
   - User story ("As a [user], I want to [action] so that [benefit]")
   - Acceptance criteria (testable conditions)
   - Priority (must-have, should-have, nice-to-have)

   Continue until user indicates feature list is complete.

4. **Non-Functional Requirements**
   Ask about:
   - Performance expectations
   - Security requirements
   - Scalability needs
   - Availability targets

5. **Technical Considerations**
   Ask about:
   - External integrations
   - Data storage requirements
   - Deployment environment
   - AI/ML components (if applicable)

6. **Write PRD**
   - Create sdlc-studio/ directory if needed
   - Use template from `templates/prd-template.md`
   - Use confidence markers: [HIGH], [MEDIUM], [LOW]
   - Include Open Questions for unresolved items

---

## /sdlc-studio prd generate - Step by Step

1. **Launch Exploration**
   Use Task tool with Explore agent:
   ```
   Explore this codebase comprehensively:
   1. Directory structure and architecture patterns
   2. README and documentation files
   3. Configuration (package.json, docker-compose, .env.example)
   4. Database schemas and migrations
   5. API routes and endpoints
   6. Test files (to understand expected behaviour)
   7. AI/ML configurations (prompts, model settings)
   Return a structured report of findings.
   ```

2. **Feature Extraction**
   From exploration, identify:
   - Core functionality implemented
   - User-facing features vs internal utilities
   - Integration points
   - Data models and relationships

3. **Infer Requirements**
   For each feature:
   - Reconstruct the likely user story
   - Document observable behaviour as acceptance criteria
   - Assess completeness (Complete, Partial, Stubbed, Broken)

4. **Technical Analysis**
   Document:
   - Architecture pattern
   - Security measures found
   - Error handling approach
   - Configuration and environment variables

5. **Write PRD**
   - Use confidence markers throughout
   - Include Technical Debt Register (TODOs, FIXMEs)
   - Include Open Questions for ambiguities

---

## /sdlc-studio prd update - Step by Step

1. **Read Existing PRD**
   - Load from sdlc-studio/prd.md
   - Parse Feature Inventory section
   - Extract features with current status

2. **Analyse Implementation**
   For each feature, use Task tool with Explore agent:
   ```
   Search for implementation of: [feature name]
   Look for:
   1. Relevant code files and functions
   2. Test coverage
   3. Documentation mentioning this feature
   4. Configuration related to this feature
   Assess: Complete, Partial, Stubbed, Broken, or Not Started?
   ```

3. **Discover New Features**
   - Look for functionality not documented
   - Check recent commits
   - Identify undocumented capabilities

4. **Update PRD**
   - Update status for each feature
   - Add newly discovered features
   - Update last-modified date
   - Add changelog entry

5. **Report Changes**
   - Features marked complete
   - Features still in progress
   - New features discovered
   - Any regressions

---

## /sdlc-studio epic - Step by Step

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

5. **Write Files**
   - Write `sdlc-studio/epics/EP{NNNN}-{slug}.md`
   - Create/update `sdlc-studio/epics/_index.md`

6. **Report**
   - Number of Epics created
   - List with IDs and titles
   - Orphan features (if any)

---

## /sdlc-studio epic update - Step by Step

1. **Load Epics**
   - Read all from sdlc-studio/epics/
   - Parse acceptance criteria and story links

2. **Check Story Status**
   For each Epic:
   - Read linked stories
   - Calculate completion percentage
   - If all stories Done → Epic Done
   - If any In Progress → Epic In Progress

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

## /sdlc-studio story - Step by Step

1. **Check Prerequisites**
   - Check sdlc-studio/personas.md exists
     - If missing: create from template, ask user to populate, STOP
   - Check sdlc-studio/definition-of-done.md exists
     - If missing: create from template
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

## /sdlc-studio story update - Step by Step

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

4. **Update Related Files**
   - Update _index.md with status counts
   - Check if Epic should be updated

5. **Report**
   - Stories completed
   - Stories in progress
   - Stories blocked
   - Regressions

---

## /sdlc-studio persona - Step by Step

1. **Check Existing**
   - Check if sdlc-studio/personas.md exists
   - If exists without --force: ask to add or replace

2. **Gather Persona Details**
   For each persona, use AskUserQuestion:
   - Persona name (memorable, humanising)
   - Role/job title
   - Technical proficiency level
   - Primary goal
   - Background (2-3 sentences)
   - Key needs (3-5 items)
   - Pain points (3-5 items)
   - Typical tasks (3-5 items)
   - Representative quote

3. **Ask for More**
   After each persona, ask to add another.
   Recommend 3-5 personas.

4. **Write Personas File**
   - Use `templates/personas-template.md`
   - Write to sdlc-studio/personas.md

5. **Report**
   - Number created
   - List with names and roles

---

## /sdlc-studio persona generate - Step by Step

1. **Analyse Codebase**
   Use Task tool with Explore agent:
   ```
   Analyse codebase to identify user types:
   1. Role/permission definitions
   2. Authentication/authorization patterns
   3. UI for different user journeys
   4. User type mentions in docs/comments
   5. Test files for user scenarios
   Return: List of user types with evidence
   ```

2. **Build Persona Drafts**
   For each user type:
   - Assign persona name
   - Infer role from code context
   - Estimate technical proficiency
   - Draft goals, needs, pain points

3. **Validate with User**
   Present drafts and ask for:
   - Corrections
   - Additional personas
   - Removals

4. **Write Personas File**
   - Mark confidence: [INFERRED] or [VALIDATED]
   - Write to sdlc-studio/personas.md

---

## /sdlc-studio persona update - Step by Step

1. **Read Existing**
   - Load sdlc-studio/personas.md
   - Parse each persona section

2. **Gather Updates**
   For each persona, ask:
   - Changes to role or proficiency?
   - New needs or pain points?
   - Tasks to add or remove?
   - Should be retired?

3. **Check for New**
   Ask if new personas needed.

4. **Update File**
   - Apply changes
   - Add new personas
   - Remove retired
   - Add revision history

---

# PRD Section Reference

Detailed guidance for completing each section of the PRD template.

---

## 1. Project Overview

### CREATE Mode - Questions to Ask
- What is the project called?
- What does it do in one sentence?
- What technologies are you using or planning to use?
- Is this a new project, MVP, or mature product?

### GENERATE Mode - What to Look For
- README.md title and description
- package.json name/description fields
- Docker/compose files for architecture clues
- Directory structure patterns (monorepo, microservices, etc.)

### UPDATE Mode - How to Assess
- Check if tech stack has changed
- Verify architecture description matches current state
- Update maturity assessment if significant progress made

---

## 2. Problem Statement

### CREATE Mode - Questions to Ask
- What problem does this solve?
- Who experiences this problem?
- What happens if the problem isn't solved?
- What existing solutions are there and why aren't they sufficient?

### GENERATE Mode - What to Look For
- README "About" or "Why" sections
- Code comments explaining purpose
- Marketing copy in docs
- Issue tracker for pain points addressed

### UPDATE Mode - How to Assess
- Rarely changes; verify still accurate
- Update if pivot or scope change occurred

---

## 3. Feature Inventory

### CREATE Mode - Questions to Ask
For each feature:
- What is the feature name?
- What does it do?
- Who uses it?
- What are the acceptance criteria? (How do we know it works?)
- What priority is it? (Must-have, should-have, nice-to-have)

### GENERATE Mode - What to Look For
- Route handlers and API endpoints
- UI components and pages
- Service classes and modules
- Test descriptions (often describe features)
- Menu items and navigation

### UPDATE Mode - How to Assess
For each feature:
- Search codebase for implementation
- Check test files for coverage
- Verify functionality manually if possible
- Update status: Complete, Partial, Stubbed, Broken, Not Started

---

## 4. Functional Requirements

### CREATE Mode - Questions to Ask
- What inputs does the system accept?
- What outputs does it produce?
- What transformations happen in between?
- What business rules apply?

### GENERATE Mode - What to Look For
- Validation logic
- Data transformations
- Business rule implementations
- Input/output schemas
- API request/response types

### UPDATE Mode - How to Assess
- Verify documented behaviours match implementation
- Add any undocumented functional requirements found

---

## 5. Non-Functional Requirements

### CREATE Mode - Questions to Ask
- **Performance:** What response times are acceptable? Expected load?
- **Security:** What data needs protection? Authentication requirements?
- **Scalability:** How many users/requests expected? Growth projections?
- **Availability:** What uptime is required? Recovery time objectives?

### GENERATE Mode - What to Look For
- Caching implementations
- Rate limiting
- Authentication middleware
- Error handling patterns
- Retry logic
- Health check endpoints
- Load balancer configs

### UPDATE Mode - How to Assess
- Check if implemented NFRs meet stated requirements
- Note any performance issues or security gaps found

---

## 6. AI/ML Specifications

### CREATE Mode - Questions to Ask
- Will this use AI/ML? Which models or APIs?
- What prompts or instructions will be used?
- How will context be managed?
- What happens when AI fails?

### GENERATE Mode - What to Look For
- API calls to OpenAI, Anthropic, etc.
- Prompt templates and system instructions
- Context window management (chunking, summarisation)
- Model configuration (temperature, max tokens)
- Fallback and retry logic
- Cost tracking

### UPDATE Mode - How to Assess
- Verify models and versions match documentation
- Check if prompts have been modified
- Update any changed parameters

---

## 7. Data Architecture

### CREATE Mode - Questions to Ask
- What data will be stored?
- What are the relationships between data types?
- How will data be persisted? (SQL, NoSQL, files)
- What's the data lifecycle?

### GENERATE Mode - What to Look For
- Database migrations
- ORM models (SQLAlchemy, Prisma, etc.)
- Schema definitions
- JSON structures in code
- Data validation schemas (Pydantic, Zod)

### UPDATE Mode - How to Assess
- Compare documented models to actual schemas
- Note any new tables or fields
- Update relationship diagrams

---

## 8. Integration Map

### CREATE Mode - Questions to Ask
- What external services will you integrate with?
- What APIs will you consume?
- Will you expose APIs for others?
- What authentication is needed for integrations?

### GENERATE Mode - What to Look For
- HTTP client calls
- SDK imports (stripe, twilio, etc.)
- Webhook handlers
- OAuth configurations
- API key environment variables

### UPDATE Mode - How to Assess
- Verify all integrations are documented
- Check for new external service calls
- Update auth methods if changed

---

## 9. Configuration Reference

### CREATE Mode - Questions to Ask
- What environment variables are needed?
- What can be configured without code changes?
- Are there feature flags?
- What's needed for deployment?

### GENERATE Mode - What to Look For
- .env.example files
- Config loading code
- Environment variable usage
- Feature flag checks
- Docker/K8s configurations

### UPDATE Mode - How to Assess
- Scan for new environment variables
- Check for removed/deprecated config
- Update defaults if changed

---

## 10. Test Coverage Analysis

### CREATE Mode - Questions to Ask
- What testing approach will you use?
- What must be tested?
- What's acceptable coverage?

### GENERATE Mode - What to Look For
- Test files and their coverage
- Test patterns (unit, integration, e2e)
- Mocking strategies
- CI test configurations
- Coverage reports

### UPDATE Mode - How to Assess
- Run coverage analysis if possible
- Note newly tested areas
- Flag reduced coverage

---

## 11. Technical Debt Register

### CREATE Mode - Questions to Ask
- Are there known shortcuts being taken?
- What will need revisiting?
- Any deprecated dependencies planned?

### GENERATE Mode - What to Look For
- TODO comments
- FIXME comments
- HACK comments
- Deprecation warnings
- Outdated dependencies
- Inconsistent patterns

### UPDATE Mode - How to Assess
- Re-scan for new TODOs
- Check if previous debt items resolved
- Update priority based on impact

---

## 12. Documentation Gaps

### CREATE Mode - Questions to Ask
- What documentation exists?
- What's the documentation standard?
- Who is the documentation audience?

### GENERATE Mode - What to Look For
- Functions without docstrings
- Complex logic without comments
- Missing README sections
- Undocumented API endpoints
- No inline type hints

### UPDATE Mode - How to Assess
- Note new undocumented features
- Check if gaps have been filled
- Update list of missing docs

---

## 13. Recommendations

### CREATE Mode - Questions to Ask
- What's the MVP vs ideal state?
- What risks should be mitigated?
- What would make this more maintainable?

### GENERATE Mode - What to Look For
- Security vulnerabilities
- Performance bottlenecks
- Maintainability issues
- Missing error handling
- Scalability concerns

### UPDATE Mode - How to Assess
- Check if previous recommendations addressed
- Add new recommendations based on current state
- Prioritise by impact and effort

---

## 14. Open Questions

### All Modes
Document anything that:
- Cannot be determined from available information
- Requires stakeholder decision
- Has multiple valid interpretations
- Needs clarification before implementation

Format:
```
- **Q:** [Question]
  **Context:** [Why this matters]
  **Options:** [If applicable]
```

---

## Appendix Guidelines

### File Tree
- Use `tree` command output or manual listing
- Limit depth to 3-4 levels
- Exclude node_modules, __pycache__, etc.

### Dependencies
- List from package.json, requirements.txt, etc.
- Group by purpose (runtime, dev, optional)

### API Catalogue
- List all exposed endpoints
- Include method, path, brief description
- Note authentication requirements

### Changelog
- Track PRD updates, not code changes
- Include date, version, summary of changes

---

# Epic Section Reference

Detailed guidance for completing each section of the Epic template.

---

## Summary

### What to Include
- 2-3 sentences describing what this Epic delivers
- Written for someone unfamiliar with the project
- Focus on user value, not technical implementation

### What to Avoid
- Technical jargon without explanation
- Implementation details (save for stories)
- Vague statements like "improve the system"

---

## Business Context

### Problem Statement
- Extract from PRD's Problem Statement
- Focus on the specific aspect this Epic addresses
- Reference PRD section for traceability

### Value Proposition
- What happens if we DO this?
- What happens if we DON'T?
- Quantify where possible

### Success Metrics
- Must be measurable
- Include baseline (current state) even if "N/A"
- Specify how measurement will occur
- Examples: completion rate, time reduction, error rate

---

## Scope

### In Scope
- Be specific about what's included
- List features, not implementation details
- Helps prevent scope creep

### Out of Scope
- Explicitly state exclusions
- Include brief rationale (helps prevent arguments later)
- Can reference "future Epic" if planned

### Affected Personas
- Link to personas.md
- Describe HOW this Epic affects each persona
- Helps prioritise and validate stories

---

## Acceptance Criteria (Epic Level)

### Format
- High-level, observable outcomes
- Use checkboxes for tracking
- NOT detailed Given/When/Then (save for stories)

### Good Examples
- [ ] Users can complete registration without assistance
- [ ] Dashboard loads within 2 seconds
- [ ] All data is encrypted at rest

### Bad Examples
- [ ] Code is written (too vague)
- [ ] Tests pass (that's DoD, not AC)
- [ ] Given user clicks button, When... (too detailed for Epic)

---

## Dependencies

### Blocked By
- Other Epics that must complete first
- External systems or APIs
- Data migrations or infrastructure
- Include impact notes (what happens if delayed)

### Blocking
- What's waiting on this Epic
- Helps prioritise and communicate urgency
- Include consequence of delay

---

## Risks & Assumptions

### Assumptions
- What are we taking for granted?
- Each should be validateable
- If assumption proves wrong, impact should be assessed

### Risks
- Technical risks (new technology, integration)
- Business risks (user adoption, market timing)
- Resource risks (availability, skills)
- Include likelihood/impact for prioritisation
- Must have mitigation strategy

---

## Technical Considerations

### Architecture Impact
- Does this require new services?
- Significant refactoring needed?
- Infrastructure changes?
- Keep high-level (details in stories)

### Integration Points
- External APIs and services
- Internal system boundaries
- Authentication/authorisation touchpoints

### Data Considerations
- New data models
- Migrations required
- Data dependencies from other systems

---

## Sizing & Effort

### Story Points
- Relative sizing (1, 2, 3, 5, 8, 13, 21)
- Based on complexity, not time
- Compare to reference Epics

### Story Count
- Estimate range (e.g., "8-12 stories")
- Helps sprint planning
- Refine after story generation

### Complexity Factors
- What makes this harder than it looks?
- New technology, integrations, unknowns
- Helps justify sizing

---

## Story Breakdown

### Before Story Generation
- Provisional titles only
- Use `- [ ] US{{TBD}}: {Title}`

### After Story Generation
- Updated automatically by `/sdlc-studio story`
- Links to actual story files
- Status tracked via story files

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

# Personas Reference

Guidance for creating effective user personas.

---

## Persona Structure

### Required Fields
- **Name**: Memorable, humanising (e.g., "Power User Pat")
- **Role**: Job title or function
- **Technical Proficiency**: Novice / Intermediate / Advanced / Expert
- **Primary Goal**: One sentence, what they want to achieve

### Background
- 2-3 sentences about who this person is
- Context that affects how they use the product
- NOT a biography

### Needs & Motivations
- What drives their behaviour?
- What are they trying to accomplish?
- Link to product features

### Pain Points
- Current frustrations
- Problems with existing solutions
- Opportunities for your product

### Typical Tasks
- What do they actually DO?
- Helps generate realistic user stories
- Prioritise common over rare tasks

### Quote
- Representative mindset
- Captures their perspective
- Humanises the persona

---

## Best Practices

### Number of Personas
- 3-5 is usually sufficient
- Too few: missing perspectives
- Too many: dilutes focus

### Validation
- Based on research, not assumptions
- Interview actual users if possible
- Update as you learn more

### Usage
- Reference in every user story
- Guides feature prioritisation
- Helps resolve design debates
