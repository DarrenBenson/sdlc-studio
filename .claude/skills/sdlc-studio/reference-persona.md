# SDLC Studio Reference - Persona

Detailed workflows for User Persona creation, management, and consultation.

<!-- Load when: creating, reviewing, or consulting Personas -->

---

# Persona Framework

## Categories {#categories}

Personas are organised into two categories:

### Team Personas

Internal team members who create and review artefacts. Organised by Three Amigos:

| Amigo | Focus | Example Roles |
|-------|-------|---------------|
| **Product** | What and Why | PM, BA, Product Owner |
| **Engineering** | How | Senior Dev, Architect, DevOps |
| **QA** | What If | QA Lead, Test Automation |

### Stakeholder Personas

External stakeholders who use the product or influence requirements:

| Category | Focus | Example Roles |
|----------|-------|---------------|
| **Users** | Day-to-day usage | Power User, Novice, Accessibility |
| **Business** | Organisational impact | Executive, Operations |
| **Technical** | Non-functional concerns | Security, Compliance |

---

## Archetype Personas {#archetypes}

Pre-built personas available in `templates/personas/`:

**Team - Product:**
- Sarah Chen (PM) - Strategic, data-driven, scope-conscious
- Alex Rivera (BA) - Detail-oriented, requirements expert

**Team - Engineering:**
- Marcus Johnson (Senior Dev) - Pragmatic, maintainability-focused
- Kai Tanaka (Junior Dev) - Learning, fresh perspective
- Nadia Okonkwo (Architect) - Systems thinking, long-term view
- Chris Morgan (DevOps) - Operations, reliability

**Team - QA:**
- Priya Sharma (QA Lead) - Risk-based testing, quality advocate
- Jordan Lee (Automation) - Test architecture, CI/CD

**Stakeholders - Users:**
- Emma Wilson (Power User) - Efficiency, keyboard shortcuts
- Tom Bradley (Novice) - Guidance, safe defaults
- Lisa Chen (Accessibility) - Screen reader, inclusive design

**Stakeholders - Business:**
- James Mitchell (Executive) - ROI, timelines
- Diana Reyes (Operations) - Day-to-day workflow, support

**Stakeholders - Technical:**
- David Park (Security) - Threats, data protection
- Rachel Kim (Compliance) - Regulations, audit readiness

---

# Persona Workflows

## /sdlc-studio persona create {#persona-create-workflow}

Interactive creation of rich, detailed personas.

1. **Check Existing**
   - Check if `sdlc-studio/personas/` directory exists
   - If exists without `--force`: ask to add or replace

2. **Select Category**
   Ask: "Is this a Team persona or Stakeholder persona?"
   - Team: Ask which amigo (Product/Engineering/QA)
   - Stakeholder: Ask type (User/Business/Technical)

3. **Gather Identity**
   - Full name (humanising, memorable)
   - Age and career stage
   - Role/job title
   - Years of experience
   - Technical proficiency level

4. **Gather Personality**
   - 3 key personality traits with descriptions
   - Communication style (formality, verbosity, directness)

5. **Gather Professional Context**
   - Background/career history (2-3 sentences)
   - Expertise areas (3-5 items)
   - Blind spots (2-3 items)

6. **Gather Psychology**
   - Primary goals (what success looks like)
   - Hidden concerns (worries they may not voice)
   - Decision drivers (values, evidence types, red flags)
   - Frustrations (3-5 items)
   - Delights (2-3 items)

7. **Gather Interaction Guide**
   - Questions they typically ask (3-5)
   - What makes them approve
   - What makes them push back
   - Representative quote

8. **Gather Backstory**
   - A specific past experience that shapes their viewpoint

9. **Offer Archetype Start**
   Before detailed questions, offer: "Would you like to start from an archetype and customise?"
   - If yes: Load archetype, ask what to change
   - If no: Proceed with full questionnaire

10. **Write Persona File**
    - Use `templates/personas/persona-template.md`
    - Write to `sdlc-studio/personas/[category]/[name].md`
    - Update `sdlc-studio/personas/index.md`

11. **Ask for More**
    After each persona, ask to add another.

---

## /sdlc-studio persona generate {#persona-generate-workflow}

Reverse engineer personas from existing artefacts.

### Source: PRD (`--from-prd`)

1. **Analyse PRD**
   Parse the PRD for:
   - Explicit user types mentioned
   - Stakeholders referenced
   - Goals and use cases that imply users
   - Personas implied but not named

2. **Present Discoveries**
   ```
   I found these potential personas in the PRD:
   1. Admin User (mentioned 12 times)
   2. Report Viewer (mentioned 8 times)
   3. [Implied] Data Analyst (from analytics use cases)

   Should I proceed with these? [Y/n/add more]
   ```

3. **Interactive Enrichment**
   For each persona:
   - "Is this a Team persona or Stakeholder?"
   - "What's their typical day like?"
   - "What frustrates them about current solutions?"
   - "How do they make decisions?"
   - "Any backstory that shapes their viewpoint?"

4. **Write Persona Files**
   - Mark as [GENERATED FROM PRD]
   - Write individual files
   - Update index

### Source: Codebase (`--from-code`)

1. **Analyse Codebase**
   Use Task tool with Explore agent:
   ```
   Analyse codebase to identify user types:
   1. Role/permission definitions (auth, RBAC)
   2. User model fields and types
   3. UI routes for different user journeys
   4. API endpoints with role-based access
   5. Test files with user scenarios
   Return: List of user types with evidence
   ```

2. **Build Persona Drafts**
   For each user type found:
   - Map to role name
   - Infer technical proficiency from UI complexity
   - Draft goals from permissions/features available

3. **Validate and Enrich**
   Present drafts, ask for corrections and additional detail.

4. **Write Persona Files**
   - Mark as [INFERRED FROM CODE]
   - Write individual files
   - Update index

### Source: Documentation (`--from-docs`)

1. **Scan Documentation**
   - README and wiki pages
   - Existing requirements documents
   - User journey documentation
   - Support documentation (who contacts support?)

2. **Extract User Types**
   - Named user types
   - Implied users from documentation audience
   - Support ticket patterns

3. **Validate and Enrich**
   As per PRD workflow.

---

## /sdlc-studio persona import {#persona-import-workflow}

Import existing persona markdown files.

1. **Read Source File**
   - Accept path to markdown file
   - Parse persona content

2. **Validate Structure**
   - Check for required sections
   - Warn about missing fields

3. **Categorise**
   Ask: "Is this a Team or Stakeholder persona?"
   - Determine amigo/type

4. **Write to Project**
   - Copy to appropriate directory
   - Update index

---

## /sdlc-studio persona list {#persona-list-workflow}

Display all personas for current project.

1. **Read Index**
   - Load `sdlc-studio/personas/index.md`

2. **Display Summary**
   ```
   TEAM PERSONAS (Three Amigos)

   Product:
     Sarah Chen (PM) - Strategic decisions, scope control
     Alex Rivera (BA) - Requirements clarity

   Engineering:
     Marcus Johnson (Senior Dev) - Technical quality

   QA:
     Priya Sharma (QA Lead) - Test strategy

   STAKEHOLDER PERSONAS

   Users:
     Emma Wilson (Power User) - Efficiency needs
     Tom Bradley (Novice) - Onboarding experience

   Business:
     James Mitchell (Exec) - ROI, timelines
   ```

---

## /sdlc-studio persona review {#persona-review-workflow}

Review and update existing personas.

1. **Read Existing**
   - Load all persona files
   - Parse each persona

2. **Gather Updates**
   For each persona:
   - "Any changes to role or context?"
   - "New concerns or frustrations?"
   - "Updated decision drivers?"
   - "Should this persona be retired?"

3. **Check for New**
   - "Are there user types not covered?"
   - "Any new team members to represent?"

4. **Update Files**
   - Apply changes
   - Add new personas
   - Archive retired (don't delete)
   - Update revision history in index

---

# Enhanced Persona Structure {#enhanced-structure}

## Required Sections

| Section | Purpose |
|---------|---------|
| Quick Reference | At-a-glance summary table |
| Identity | Who they are, personality, communication |
| Professional Context | Background, expertise, blind spots |
| Psychology | Goals, concerns, decision drivers |
| Interaction Guide | Questions, approval/rejection triggers |
| Backstory | Humanising past experience |

## Template Location

`templates/personas/persona-template.md`

---

# Value and Cost {#value-and-cost}

## When to Use Personas

| Artefact | Value | Default |
|----------|-------|---------|
| PRD Review | HIGH - catches missing requirements early | On |
| Story Acceptance Criteria | HIGH - validates user needs | On |
| Trade-off Decisions | HIGH - reveals true priorities | On |
| Epic Scoping | MEDIUM - impact assessment | On request |
| Technical Spec | MEDIUM - non-functional concerns | On request |
| Individual Stories | LOW - unless complex | Off |

## Cost Controls

- `--quick` - Brief feedback, fewer tokens
- `--skip-personas` - Bypass persona consultation
- `--persona [name]` - Consult specific persona only

---

# File Structure {#file-structure}

```
sdlc-studio/
  personas/
    index.md                    # Project persona index
    team/
      product/
        sarah-chen-pm.md
      engineering/
        marcus-johnson-senior.md
      qa/
        priya-sharma-qa-lead.md
    stakeholders/
      users/
        emma-wilson-power.md
      business/
        james-mitchell-exec.md
      technical/
        david-park-security.md
```

---

# See Also

- `reference-consult.md` - Consultation workflows (Phase 2)
- `reference-prd.md` - PRD workflows
- `reference-story.md` - Story workflows (personas referenced)
- `reference-decisions.md` - Ready criteria
- `help/persona.md` - Quick command reference

---

## Navigation {#navigation}

**Prerequisites:**
- `reference-philosophy.md#create-mode` OR `#generate-mode` - Understanding modes

**Related workflows:**
- `reference-prd.md` - Product Requirements (upstream)
- `reference-story.md` - User Stories (downstream - personas referenced)

**Cross-cutting concerns:**
- `reference-decisions.md` - Decision guidance
- `reference-outputs.md` - File formats and status values

**Future (Phase 2+):**
- `reference-consult.md` - Consultation commands
- `reference-chat.md` - Interactive sessions
