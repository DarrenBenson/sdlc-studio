# SDLC Studio Reference - Persona

Detailed workflows for User Persona creation, management, and consultation.

<!-- Load when: creating, reviewing, or consulting Personas -->

## Which persona doc? {#which-doc}

| You want to... | Read |
| --- | --- |
| Define who the product is *for* (a goal-directed **design persona**) | this file + `templates/personas/persona-template.md` |
| Reverse-engineer personas from existing code / users | `reference-persona-generate.md` |
| Set up a **review seat** that critiques artefacts (Three Amigos, PO/PM owners) | `reference-workflow-personas.md` + `templates/personas/amigo-template.md` (the enriched seat schema) |
| Consult personas or seats on an artefact | `reference-consult.md` |
| Run an interactive persona session | `reference-chat.md` |

**Design personas** (who the product serves) and **review seats** (who reviews the work) are
distinct - see `reference-workflow-personas.md#document-owner-seats`.

---

# Persona Framework

## The cast (goal-directed design personas) {#categories}

A persona is a **specific, goal-directed person** the product serves - defined by its **goals**,
not demographics (Alan Cooper's model). Use the full **cast**; the **Primary** is the one
the product is designed *for*.

| Cast role | What it is |
| --- | --- |
| **Primary** | The single precise individual the product is designed for (one per product/epic) |
| **Secondary** | Mostly served by the primary design, with one or two extra needs |
| **Supplemental** | Fully covered by the primary design; listed for completeness |
| **Negative** | The anti-persona - explicitly *not* designed for |
| **Customer** | Buys or authorises but does not use |
| **Served** | Affected by the product without using it |

Only **Primary + Negative** are mandatory; add the rest as the product needs them.

**Goals define the persona.** Each carries ordered **End goals** (what they accomplish, most
important first - the design is judged against these) and **Experience goals** (how they want to
feel). The full schema is under [Enhanced Persona Structure](#enhanced-structure).

> **Design personas vs review seats.** This cast is the product's *users* - who you design for.
> The internal *review seats* that critique artefacts (the Three Amigos: Product / Engineering /
> QA) are a separate concern - their substrate and consult mechanics are covered separately. A
> goal-directed design persona is good input to that system, but is not the same thing.

---

## Archetype Personas {#archetypes}

> These are **review-seat** seeds (consult roles that critique artefacts), not the
> goal-directed design cast above. Design personas describe the product's users; review seats
> describe who reviews the work.

**Archetype seeds** (role + one-line disposition). The skill ships these seeds plus
`templates/personas/persona-template.md`; `persona create` generates the full persona
on demand for the consuming project rather than baking ~1680 lines of invented
backstory into every install. To use one, run `persona create` from its
seed and customise.

> **Migration:** the 15 pre-built character files under
> `templates/personas/stakeholders/` and `team/` were removed. A consuming project that
> referenced those files should regenerate the personas it needs via `persona create`
> from the seeds below (its own `sdlc-studio/personas/` are unaffected).

**Team - Product:**

- Sarah Chen (PO) - Strategic, data-driven, scope-conscious
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

Interactive creation of a goal-directed, well-formed persona (the Cooper model).

1. **Check Existing**
   - Check if `sdlc-studio/personas/` directory exists
   - If exists without `--force`: ask to add or replace

2. **Choose Cast Role**
   Ask which role in the cast: Primary / Secondary / Supplemental / Negative / Customer / Served.
   Start with the **Primary** (the one the product is designed for); only Primary + Negative are
   mandatory.

3. **Gather Identity**
   - Full name (a specific, memorable individual - not a type)
   - Role / job title
   - One-line context (where and how they work)

4. **Gather End Goals**
   - What they are trying to accomplish, as an **ordered** list (most important first)
   - These are the design target - the product is judged against them

5. **Gather Experience Goals**
   - How they want to feel while using it (in control, unhurried, not made to feel stupid)

6. **Gather Behaviours & Context**
   - Environment (device, setting, interruptions, constraints)
   - Frequency / pressure of use
   - Proficiency (what they know well, what they avoid)

7. **Gather Frustrations**
   - What trips them up with the current tools or status quo

8. **Gather a Scenario**
   - A short narrative of the persona using the product to reach an End goal, in context

9. **Offer Archetype Start**
   Offer: "Start from an archetype seed and customise?" - if yes, seed from `#archetypes` +
   `persona-template.md`, then refine to the cast role and goals above.

10. **Write Persona File**
    - Use `templates/personas/persona-template.md` (fill every section - that is "well-formed")
    - Write to `sdlc-studio/personas/[name].md`
    - Update `sdlc-studio/personas/index.md`

11. **Ask for More**
    After each persona, ask to add another (e.g. the Negative persona, then Secondary).

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
   For each persona, fill the Cooper schema:
   - "Which cast role - Primary, Secondary, Supplemental, Negative, Customer, Served?"
   - "What are they trying to accomplish, most important first?" (ordered End goals)
   - "How do they want to feel using it?" (Experience goals)
   - "What's their environment and how often do they use it?" (behaviours & context)
   - "What frustrates them about current solutions?"
   - "Walk me through one time they'd use this." (scenario)

4. **Write Persona Files**
   - The generated file is a draft; the author fleshes it to **well-formed** (every section filled)
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
   - Assign a cast role (the main one is usually the Primary)
   - Draft ordered End goals from the permissions / features available to that type
   - Infer behaviours & context (proficiency) from UI complexity

3. **Enrich to Well-Formed**
   Present drafts, ask for corrections and the missing Cooper sections (Experience goals,
   frustrations, a scenario).

4. **Write Persona Files**
   - The generated file is a draft; the author fleshes it to well-formed
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

3. **Assign Cast Role**
   Ask which cast role it fills (Primary / Secondary / Supplemental / Negative / Customer /
   Served), and note any sections missing for it to be well-formed.

4. **Write to Project**
   - Copy into `sdlc-studio/personas/`
   - Update index

---

## /sdlc-studio persona list {#persona-list-workflow}

Display all personas for current project.

1. **Read Index**
   - Load `sdlc-studio/personas/index.md`

2. **Display Summary** (grouped by cast role)

   ```
   PRIMARY (the design target)
     Emma Wilson (Power User) - file a claim in under two minutes

   SECONDARY
     Tom Bradley (Occasional User) - same flow, needs more guidance

   NEGATIVE (not designed for)
     Batch-integrator - wants a bulk API, deliberately out of scope

   CUSTOMER / SERVED
     James Mitchell (Buyer) - ROI, rollout risk
   ```

   Flag any persona that is not yet **well-formed** (missing a schema section).

---

## /sdlc-studio persona review {#persona-review-workflow}

Review and update existing personas.

1. **Read Existing**
   - Load all persona files
   - Run `validate.py personas` to flag any not-well-formed for its cast role (advisory)

2. **Gather Updates**
   For each persona:
   - "Any changes to cast role or context?"
   - "Have the End goals changed, or their order?"
   - "New frustrations, or a better scenario?"
   - "Is it still well-formed (every section filled)?"
   - "Should this persona be retired?"

3. **Check for New**
   - "Are there user types not covered by the cast?"
   - "Is the Negative persona still right (who are we deliberately not serving)?"

4. **Update Files**
   - Apply changes
   - Add new personas
   - Archive retired (don't delete)
   - Update revision history in index

5. **Clear Provisional Labels** (generated seats and stakeholders)
   - `scripts/persona_gen.py classify --root .` lists any card still
     provisional-unverified (generated, never operator-reviewed)
   - Walk each with the operator; on acceptance run
     `scripts/persona_gen.py accept --file <card>` - the stamp becomes a dated
     reviewed marker (Cooper's rule: an assumption persona stays labelled until
     validated). A card the operator edits is already promoted to authored.

---

# Enhanced Persona Structure {#enhanced-structure}

## Required Sections (a well-formed persona)

A persona is **well-formed** when it has all of (the Cooper goal-directed schema):

| Section | Purpose |
| --- | --- |
| Quick Reference | cast role, job title, one-line context |
| Who They Are | a specific named individual, not a demographic average |
| End Goals | ordered - what they accomplish; the design is judged against these |
| Experience Goals | how they want to feel using it |
| Behaviours & Context | environment, frequency, proficiency |
| Frustrations | what trips them up with the status quo |
| Scenario | a short narrative of the persona reaching an End goal in context |

"Well-formed" is **structural** (the file has these sections), not evidential - sdlc-studio does
not require research backing, and builds no authored-identity machinery.

**Cast-role variants.** A **Negative** persona swaps End Goals for *End Goals (stated to exclude)*
and replaces Experience Goals + Scenario with *Why we are not designing for them* + *how to handle
a request from them*. For **Customer / Served**, Experience Goals and Scenario are optional. See
the template's "Cast-role variants" note.

**Checking it.** `python3 "$CLAUDE_SKILL_DIR/scripts/validate.py" personas` flags a persona that is
missing a section for its cast role (advisory - it never blocks, and it allows the Negative and
Customer/Served variants). `persona review` runs it.

## Template Location

`templates/personas/persona-template.md`

---

# Value and Cost {#value-and-cost}

## When to Use Personas

| Artefact | Value | Default |
| ---------- | ------- | --------- |
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
    index.md                    # Project persona index (cast role per persona)
    emma-wilson-power-user.md   # Primary
    tom-bradley-occasional.md   # Secondary
    batch-integrator.md         # Negative (deliberately not designed for)
    james-mitchell-buyer.md     # Customer
```

A flat `personas/` directory; each file declares its cast role in its Quick Reference. (Design
personas only - review seats live with the consult workflow.)

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
