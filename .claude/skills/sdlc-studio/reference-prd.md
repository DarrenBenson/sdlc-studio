# SDLC Studio Reference - PRD

Detailed workflows for Product Requirements Document creation and management.

<!-- Load when: creating or reviewing PRD -->

---

# PRD Workflows

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

## /sdlc-studio prd review - Step by Step

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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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

### REVIEW Mode - How to Assess
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


# See Also

- `reference-trd.md` - TRD workflows
- `reference-persona.md` - Persona workflows
- `reference-architecture.md` - Architecture guidance for TRD
- `reference-epic.md` - Epic generation (next step after PRD)
- `reference-decisions.md` - Ready criteria, decision guidance
