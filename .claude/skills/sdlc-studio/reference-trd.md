# SDLC Studio Reference - TRD

Detailed workflows for Technical Requirements Document creation and management.

<!-- Load when: creating or reviewing TRD -->

---

# TRD Workflows

## /sdlc-studio trd create - Step by Step

1. **Check Prerequisites**
   - Verify PRD exists at sdlc-studio/prd.md
   - If PRD missing, prompt: "Run `/sdlc-studio prd` first"
   - Load `reference-architecture.md` for guidance

2. **Classify Project Type**
   Use decision tree from reference-architecture.md:
   - Q1: Does this serve a web frontend? -> Web Application
   - Q2: Exposes APIs for other systems? -> API Backend / Mobile Backend
   - Q3: Multiple deployable services? -> Add Monorepo modifier
   - Q4: Library/SDK? -> SDK/Library
   - Else: Desktop/CLI Application

   Document classification rationale.

3. **Present Architecture Recommendations**
   Based on project type, present defaults from reference-architecture.md:
   ```
   Based on your project type ({{type}}), recommended stack:

   **Architecture:** {{pattern}} ({{rationale}})
   **Language:** {{language}}
   **Backend:** {{framework}}
   **Database:** {{database}}
   **API Style:** {{style}}

   Would you like to:
   1. Accept these recommendations
   2. Customise selections
   3. Learn more about alternatives
   ```

4. **Gather Architecture Context**
   Use AskUserQuestion to collect:
   - Accept recommendations or customise?
   - If customising: What architecture pattern? (monolith, microservices, serverless, etc.)
   - What is the primary language and framework?
   - What database/storage approach?
   - What are the key integration points?

5. **Technology Stack Discussion**
   For each technology choice, ask:
   - What problem does this solve?
   - What alternatives were considered?
   - What are the trade-offs?

   **Require strong justifications** - "familiarity" alone is insufficient.
   See reference-architecture.md for guidance on strong vs weak rationale.

6. **API Design**
   Ask about:
   - REST, GraphQL, gRPC, or other?
   - Authentication approach (JWT, OAuth, API keys)
   - Versioning strategy
   - Rate limiting requirements

7. **Data Architecture**
   Ask about:
   - Data models and relationships
   - Storage strategy (SQL, NoSQL, hybrid)
   - Migration approach
   - Data lifecycle and retention

8. **Infrastructure Approach**
   Ask about:
   - Deployment topology (containers, VMs, serverless)
   - Environment strategy (dev, staging, prod)
   - Scaling approach
   - Disaster recovery

9. **Security Considerations**
   Ask about:
   - Threat model (who might attack, how)
   - Data classification (PII, sensitive, public)
   - Compliance requirements (GDPR, SOC2, etc.)
   - Security controls planned

10. **Write TRD**
    - Use template from `templates/trd-template.md`
    - Include Project Classification section
    - Include Architecture Checklist section
    - Reference PRD sections where appropriate
    - Document key decisions as ADRs
    - Write to sdlc-studio/trd.md

---

## /sdlc-studio trd generate - Step by Step

1. **Load Architecture Guidance**
   - Load `reference-architecture.md` for assessment criteria
   - Prepare to detect project type and patterns

2. **Launch Exploration**
   Use Task tool with Explore agent:
   ```
   Explore this codebase comprehensively for technical architecture:
   1. Directory structure and module organisation
   2. Configuration files (docker-compose, k8s, terraform, etc.)
   3. Database schemas, migrations, ORM models
   4. API routes and endpoints
   5. Authentication/authorization implementation
   6. External service integrations (SDKs, API clients)
   7. Build and deployment configuration
   8. Environment variables and secrets management
   Return a structured report of findings.
   ```

3. **Classify Project Type**
   Detect project type using pattern indicators:
   - Web frontend files (React, Vue, HTML) -> Web Application
   - API routes without frontend -> API Backend
   - Mobile SDK integrations, push services -> Mobile Backend
   - /cmd/ directory (Go), CLI entrypoints -> Desktop/CLI Application
   - setup.py, Cargo.toml with lib -> SDK/Library
   - Multiple service directories -> Monorepo

4. **Architecture Pattern Detection**
   From exploration, identify:
   - Architecture pattern (monolith, microservices, etc.)
   - Component boundaries and responsibilities
   - Communication patterns (sync, async, events)
   - Data flow between components

   Use pattern indicators from reference-architecture.md:
   - Dockerfile/docker-compose -> Containerised
   - serverless.yml/terraform -> Serverless/IaC
   - /services/ or /apps/ -> Multi-service
   - /src/routes/ or /api/ -> REST patterns

5. **Technology Stack Extraction**
   Document:
   - Core runtime (Node.js, Python, Go, etc.)
   - Frameworks (FastAPI, Express, etc.)
   - Database systems
   - Message queues / event buses
   - Cloud services

6. **API Contract Discovery**
   - Extract endpoint definitions
   - Infer request/response schemas
   - Document authentication requirements
   - Note API versioning approach

7. **Data Architecture Analysis**
   - Map database schemas
   - Document model relationships
   - Identify data stores and their purposes
   - Note migration patterns

8. **Integration Mapping**
   - List external services
   - Document protocols and authentication
   - Note retry/fallback patterns
   - Map event flows

9. **Infrastructure Analysis**
   - Document deployment approach
   - Identify environment configuration
   - Note scaling mechanisms
   - Document health checks and monitoring

10. **Security Assessment**
    - Document auth implementation
    - Note data protection measures
    - Identify potential vulnerabilities
    - List compliance considerations

11. **Architecture Assessment**
    Evaluate against best practices from reference-architecture.md:

    **Smell Detection:**
    Check for architecture smells:
    - Big Ball of Mud (>50 files in root, no layers)
    - Distributed Monolith (services deploy together)
    - Hardcoded Config (secrets in code)
    - Missing Error Handling
    - Circular Dependencies
    - God Objects (>1000 line files)

    **Pattern Alignment:**
    - Does pattern match project type?
    - Are deviations justified?
    - Is technology selection appropriate?

    **Output format:**
    ```markdown
    ## Architecture Assessment

    **Detected Pattern:** {{pattern}}
    **Detected Project Type:** {{type}}

    ### Alignment with Best Practices

    | Aspect | Finding | Status |
    |--------|---------|--------|
    | Pattern matches project type | {{observation}} | Good/Warning/Issue |
    | Clear layer separation | {{observation}} | Good/Warning/Issue |
    | API standards | {{observation}} | Good/Warning/Issue |
    | Database choice | {{observation}} | Good/Warning/Issue |

    ### Architecture Smells

    | Smell | Found | Notes |
    |-------|-------|-------|
    | {{smell}} | Yes/No | {{details}} |

    ### Recommendations

    1. [SEVERITY] {{recommendation}}
    ```

12. **Write TRD**
    - Use template from `templates/trd-template.md`
    - Include Project Classification section
    - Include Architecture Checklist section
    - Include Architecture Assessment section (from step 11)
    - Use confidence markers: [HIGH], [MEDIUM], [LOW], [INFERRED]
    - Document key choices as ADRs
    - Document Open Technical Questions
    - Write to sdlc-studio/trd.md

---

## /sdlc-studio trd review - Step by Step

1. **Read Existing TRD**
   - Load from sdlc-studio/trd.md
   - Parse each section
   - Note current architecture decisions

2. **Analyse Implementation Changes**
   Use Task tool with Explore agent:
   ```
   Compare current codebase against TRD:
   1. New services or components added?
   2. Technology stack changes?
   3. API contract modifications?
   4. Database schema changes?
   5. New integrations?
   6. Infrastructure changes?
   Return: List of changes with evidence
   ```

3. **Update TRD Sections**
   For each change found:
   - Update relevant section
   - Add ADR entry for significant decisions
   - Update Open Technical Questions
   - Resolve questions that have been answered

4. **Validate Consistency**
   - Check TRD aligns with PRD
   - Verify architecture supports all PRD features
   - Note any gaps or conflicts

5. **Write Updated TRD**
   - Update last-modified date
   - Add changelog entry
   - Preserve previous ADR history

6. **Report Changes**
   - Architecture changes documented
   - New decisions recorded
   - Questions resolved
   - Any inconsistencies with PRD

---


# See Also

- `reference-prd.md` - PRD workflows (prerequisite)
- `reference-persona.md` - Persona workflows
- `reference-architecture.md` - Architecture patterns and guidance
- `reference-epic.md` - Epic generation (next step after TRD)
- `reference-decisions.md` - Decision impact matrix, TRD decisions
