# SDLC Studio Reference - Persona

Detailed workflows for User Persona creation and management.

<!-- Load when: creating or reviewing Personas -->

---

# Persona Workflows

## /sdlc-studio persona - Step by Step {#persona-workflow}

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
   - Use `templates/core/personas.md`
   - Write to sdlc-studio/personas.md

5. **Report**
   - Number created
   - List with names and roles

---

## /sdlc-studio persona generate - Step by Step {#persona-generate-workflow}

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

## /sdlc-studio persona review - Step by Step {#persona-review-workflow}

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

# Personas Reference

Guidance for creating effective user personas.

---

## Persona Structure {#persona-structure}

### Required Fields {#required-fields}
- **Name**: Memorable, humanising (e.g., "Power User Pat")
- **Role**: Job title or function
- **Technical Proficiency**: Novice / Intermediate / Advanced / Expert
- **Primary Goal**: One sentence, what they want to achieve

### Background {#background}
- 2-3 sentences about who this person is
- Context that affects how they use the product
- NOT a biography

### Needs & Motivations {#needs-and-motivations}
- What drives their behaviour?
- What are they trying to accomplish?
- Link to product features

### Pain Points {#pain-points}
- Current frustrations
- Problems with existing solutions
- Opportunities for your product

### Typical Tasks {#typical-tasks}
- What do they actually DO?
- Helps generate realistic user stories
- Prioritise common over rare tasks

### Quote {#quote}
- Representative mindset
- Captures their perspective
- Humanises the persona

---

## Best Practices {#best-practices}

### Number of Personas {#number-of-personas}
- 3-5 is usually sufficient
- Too few: missing perspectives
- Too many: dilutes focus

### Validation {#validation}
- Based on research, not assumptions
- Interview actual users if possible
- Update as you learn more

### Usage {#usage}
- Reference in every user story
- Guides feature prioritisation
- Helps resolve design debates

---


# See Also

- `reference-prd.md` - PRD workflows
- `reference-trd.md` - TRD workflows
- `reference-story.md` - Story workflows (personas used here)
- `reference-decisions.md` - Ready criteria

---

## Navigation {#navigation}

**Prerequisites (load these first):**
- `reference-philosophy.md#create-mode` OR `reference-philosophy.md#generate-mode` - Understanding modes

**Related workflows:**
- `reference-prd.md` - Product Requirements (upstream - provides context for personas)
- `reference-story.md` - User Stories (downstream - personas referenced in every story)

**Cross-cutting concerns:**
- `reference-decisions.md` - Decision guidance and Ready criteria
- `reference-outputs.md#output-formats` - File formats and status values

**Deep dives (optional):**
- `reference-epic.md` - Epic workflows (personas used for scoping)
