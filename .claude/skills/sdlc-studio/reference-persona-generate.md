# SDLC Studio Reference - Persona Generate

<!-- Load when: user runs /sdlc-studio persona generate (from PRD, code, or docs) -->

Detailed workflows for reverse engineering personas from existing artefacts.

---

# Overview

The generate command reverse engineers personas from existing sources rather than creating from scratch. It uses a three-phase approach:

1. **Discovery** - Analyse source for potential personas
2. **Enrichment** - Interactive questioning to add depth
3. **Categorisation** - Assign to Team/Stakeholder and amigo/type

---

# Source Modes

## From PRD (`--from-prd`) {#from-prd}

Best for: Projects with existing requirements documentation.

### Step 1: Analyse PRD

Read the PRD and extract:

| Look For | Examples |
| ---------- | ---------- |
| Explicit user types | "Admin users can...", "End users will..." |
| Stakeholder mentions | "Marketing team requires...", "Finance needs..." |
| Role-based features | "Managers can approve...", "Analysts can export..." |
| Use case actors | "The customer initiates...", "Support staff responds..." |
| Implied personas | Features that imply a user type without naming it |

### Step 2: Present Discoveries

```
I've analysed the PRD and found these potential personas:

EXPLICIT (mentioned by name):
  1. Admin User - mentioned 12 times
     Evidence: "Admin users can manage settings", "Admins approve requests"

  2. Report Viewer - mentioned 8 times
     Evidence: "Report viewers can access dashboards", "read-only access"

INFERRED (implied but not named):
  3. Data Analyst - inferred from analytics features
     Evidence: "export to CSV", "custom date ranges", "pivot tables"

  4. Approver - inferred from workflow features
     Evidence: "approval workflow", "escalation paths"

Should I proceed with these personas?
  [Yes] - Continue with enrichment
  [Add more] - I'll suggest additional personas to consider
  [Remove some] - Let me know which to skip
```

### Step 3: Interactive Enrichment

For each confirmed persona, ask enrichment questions:

```
Let's enrich "Admin User":

CATEGORISATION
1. Is this a Team persona or Stakeholder?
   [Team] - Internal team member (will assign to Product/Engineering/QA)
   [Stakeholder] - External user or business stakeholder

2. (If Stakeholder) What type?
   [User] - Uses the product directly
   [Business] - Business stakeholder (exec, operations)
   [Technical] - Technical stakeholder (security, compliance)

IDENTITY
3. What name should we use? (e.g., "Admin Alice", "System Admin Sam")
   Default: Admin User → suggest "Sam Torres"

4. Approximate age and experience level?
   [Junior/Entry] - 1-3 years
   [Mid-level] - 4-7 years
   [Senior] - 8-15 years
   [Executive] - 15+ years

5. Technical proficiency?
   [Novice] [Intermediate] [Advanced] [Expert]

CONTEXT
6. What's their typical day like when using this system?

7. What frustrates them about current solutions?

8. How do they make decisions about tools and processes?

BACKSTORY
9. Any specific past experience that shapes how they approach this?
   (e.g., "Previously used a system that had a major security breach")
```

### Step 4: Write Persona Files

- Create individual files in `sdlc-studio/personas/[category]/`
- Mark as `[GENERATED FROM PRD]` in metadata
- Update `sdlc-studio/personas/index.md`

---

## From Codebase (`--from-code`) {#from-code}

Best for: Brownfield projects with existing authentication/authorisation.

### Step 1: Analyse Codebase

Use Task tool with Explore agent:

```
Analyse the codebase to identify user types. Search for:

1. AUTHENTICATION & AUTHORISATION
   - User model/schema definitions
   - Role enums or constants
   - Permission definitions
   - RBAC configurations
   - Auth middleware/guards

2. USER INTERFACE PATTERNS
   - Route definitions with role guards
   - Conditional UI based on user type
   - Different dashboards/landing pages
   - Feature flags by user type

3. API PATTERNS
   - Endpoints with role-based access
   - Different response shapes by role
   - Rate limits by user type

4. DOCUMENTATION & TESTS
   - README mentions of user types
   - Test fixtures with user personas
   - Comments describing user scenarios

Return for each user type found:
- Name/identifier used in code
- Evidence locations (file:line)
- Permissions/capabilities
- UI routes accessible
- Estimated technical proficiency (based on UI complexity)
```

### Step 2: Present Discoveries

```
I've analysed the codebase and found these user types:

FROM CODE (role definitions):
  1. ADMIN
     Source: src/auth/roles.ts:12
     Permissions: ["manage_users", "view_audit_log", "system_config"]
     UI Routes: /admin/*, /settings/*

  2. MANAGER
     Source: src/auth/roles.ts:18
     Permissions: ["approve_requests", "view_team_reports", "manage_team"]
     UI Routes: /dashboard, /team/*, /reports/*

  3. USER
     Source: src/auth/roles.ts:24
     Permissions: ["create_request", "view_own_data"]
     UI Routes: /home, /requests/*, /profile

FROM UI PATTERNS (inferred):
  4. REPORT_VIEWER (read-only variant)
     Evidence: src/components/ReportDashboard.tsx - checks for viewOnly prop
     Likely: Stakeholder who needs visibility but not edit access

Shall I proceed with these personas?
```

### Step 3: Map to Personas

For each code role:

```
Let's map "ADMIN" to a persona:

1. Is this a Team persona or Stakeholder?
   Context: Has system configuration access, manages users
   Suggestion: [Team - Engineering] - Likely a DevOps or platform engineer

2. What human name should we use?
   Suggestion: Chris Morgan (DevOps archetype match)
   Or create new: ___

3. The code shows these capabilities:
   - manage_users
   - view_audit_log
   - system_config

   What's the real-world context? What problem are they solving?

4. Technical proficiency?
   Based on UI complexity: [Expert] - Admin UI has advanced features
   Confirm or adjust: ___
```

### Step 4: Validate Against Archetypes

```
This persona seems similar to an existing archetype:

  Chris Morgan (DevOps Engineer)
  - Focus: Deployment, monitoring, infrastructure
  - Technical Level: Expert

Would you like to:
  [Use archetype] - Start from Chris Morgan, customise for this project
  [Create new] - Build a distinct persona for this project's admin
```

---

## From Documentation (`--from-docs`) {#from-docs}

Best for: Projects with existing user documentation or support processes.

### Step 1: Scan Documentation

Look for:

| Source | What to Extract |
| -------- | ----------------- |
| README.md | Installation for different user types, quick start guides |
| Wiki/Docs | User guides targeting specific audiences |
| Support docs | Who contacts support? Common issues by user type |
| Training materials | Different curricula for different roles |
| Release notes | Features "for admins", "for end users" |

### Step 2: Present Discoveries

```
I've scanned the documentation and found these user types:

FROM USER GUIDES:
  1. Getting Started Guide - targets "new users"
     Evidence: docs/getting-started.md
     Profile: Needs hand-holding, basic features only

  2. Admin Guide - targets "system administrators"
     Evidence: docs/admin-guide.md
     Profile: Technical, manages configuration

FROM SUPPORT PATTERNS:
  3. "Power users" mentioned in FAQ
     Evidence: docs/faq.md - "For power users who want keyboard shortcuts..."
     Profile: Efficiency-focused, advanced features

FROM TRAINING:
  4. Manager Training curriculum
     Evidence: training/manager-track.md
     Profile: Team oversight, reporting needs
```

### Step 3: Enrichment

Same enrichment flow as PRD mode.

---

# Enrichment Question Bank {#enrichment-questions}

## Quick Mode (`--quick`)

Minimal questions for fast persona creation:

1. Team or Stakeholder?
2. Name?
3. One-line description?
4. Primary goal?

## Standard Mode (default)

Balanced depth:

1. Category (Team/Stakeholder)
2. Type (Amigo or Stakeholder type)
3. Name and age range
4. Technical proficiency
5. Primary goal
6. Top 3 frustrations
7. How they make decisions
8. Representative quote

## Thorough Mode (`--thorough`)

Full persona development:

All standard questions plus:

- Full background story
- 3 personality traits with examples
- Communication style details
- Expertise areas and blind spots
- Hidden concerns
- Detailed decision drivers
- Backstory incident
- Typical questions they ask

---

# Team and Stakeholder Generation {#team-generation}

The working TEAM (`--team`) and the stakeholder panel (`--stakeholders`) are generated
from the project itself - fresh named individuals per project, never the same cast twice.
Model-driven judgement inside a deterministic frame: analysis maps onto **behavioural
variables and risk axes, never demographics**; the mechanical floor is owned by scripts.

## `--team` {#team}

### Step 1: Analyse (every source that exists; degrade honestly when absent)

Read the PRD (domain, user classes, compliance vocabulary), TRD (stack, architecture),
TSD + `.config.yaml` (quality bar, depth tiers), `repo_map.py build` output (languages,
frameworks, test runners), and the design-persona cast if present. With only a repo
available (the brownfield taster), analyse the repo map alone and say so. Present a
**discoveries table**: domain, stack, risk signals, quality bar - each row marked
`inferred` or `unknown`.

### Step 2: Ask when unsure - HARD-CAPPED at 4 questions (1 under `--quick`)

Multi-choice, one at a time, ONLY for signals the analysis could not settle:

1. **Domain risk class** (asked unless unambiguous): money-movement / PII-health /
   uptime-SLA / low-stakes. This one answer flavours every seat's paranoia and drives
   extra-seat proposals.
2. **Compliance regime** - asked ONLY when the risk-class answer implies one.
3. **Extra seats** - one multi-select confirm, proposed ONLY on strong signals
   (Security for auth/payments/PII; SRE for infra-heavy; Data for pipelines/ML; UX for
   consumer surface), cap +2. The cast stays 3-5 - proliferation is the documented
   persona failure mode.
4. **Anything to adjust?** - one batch prompt showing every remaining inference with its
   default. Every inference is contestable here; none is individually prompted.

Headless runs take the defaults and keep the provisional stamp (Step 4).

### Step 3: Generate fresh named individuals

One card per role into `sdlc-studio/personas/seats/<name>.md` on the
`templates/personas/amigo-template.md` schema: declared `<!-- role: ... -->`, dual
render, and Craft Goals / Non-Negotiables / Pushes-Back-When / Shadow grounded in THIS
project's stack, domain and risk class (a payments QA is paranoid about idempotency and
reconciliation; a game QA about frame budgets and input latency). A characteristic that
influences no engineering decision is omitted.

**Shadowing guard:** if any `personas/amigos/<role>.md` claims a generated role, STOP and
run the migration first (`project_upgrade.py --apply` migrates it to `seats/`), or report
the conflict - never generate into a home that a legacy card would out-resolve. Applies
under `--dry-run` too.

**Never-clobber:** classify every existing seat card first
(`persona_gen.py classify --root .`): `authored` and `generated-edited` cards are NEVER
overwritten - offer an enrichment diff instead. `generated-pristine` cards of the same
role are regenerated in place (a re-run diffs its own prior). `--dry-run` reports what
would be written, asked, and skipped.

### Step 4: Stamp, gate, accept

1. Stamp every written card: `persona_gen.py stamp --file <card>` (provisional-unverified
   with the content hash).
2. Run the mechanical floor: `validate.py seats` - any error (missing role, missing
   review render, demographic token, duplicate role, cast > 5) is fixed before the flow
   may complete.
3. **Batch-accept close** (interactive runs): present the team, one confirm; on yes run
   `persona_gen.py accept --root .` for the TEAM cards - the flow ends with the squad
   standing, not with an asterisk. Headless/`--quick` runs skip acceptance; the stamp
   stays and `status` surfaces the count until `persona review` clears it.

## `--stakeholders` {#stakeholders}

Same four steps; differences: the cast question is one multi-select (economic buyer,
compliance, ops/support, served-but-not-using groups); cards go to
`sdlc-studio/personas/stakeholders/<name>.md` on
`templates/personas/stakeholder-template.md` (goals, veto lines, evidence they read,
Cooper Customer/Served designation, and the arbitration rule ON the card: buyer goals
never override the Primary user's interface). Stakeholder cards KEEP the provisional
stamp until `persona review` - they are assumption personas until validated (Cooper's
rule). `consult stakeholders` names any provisional card in its output header.

## Standalone invocation {#team-standalone}

`persona generate --team` needs no PRD: with only a repository it analyses the repo map
and asks the risk-class question. Offered after `prd create`/`generate`, at
`project upgrade` (before the default-amigo option), and worth running after a
`review generate` taster.

# Validation Rules {#validation}

Before writing personas, validate:

| Check | Rule |
| ------- | ------ |
| Minimum personas | At least 1 Team, 1 Stakeholder |
| Coverage | All Three Amigos represented if Team personas exist |
| Uniqueness | No duplicate names or near-identical roles |
| Completeness | All required fields populated |
| Consistency | Technical levels make sense for roles |

---

# Output Format {#output}

## File Structure

```
sdlc-studio/personas/
├── index.md                          # Updated with new personas
├── [name-slug].md                    # Design personas: flat Cooper layout (validated)
├── seats/
│   └── [name-slug].md               # Working team seats (declared `<!-- role: ... -->`;
│                                    #  the converged home the resolver reads)
└── stakeholders/
    └── [name-slug].md               # Stakeholder panel (flat; read by consult)
```

## Persona File Header

```markdown
<!--
Source: Generated from PRD
Generated: 2024-01-15
Confidence: INFERRED / VALIDATED
Last Review: 2024-01-15
-->
```

## Index Update

Add to appropriate section with source annotation:

```markdown
| Sam Torres | Admin | System configuration, user management | [Details](team/engineering/sam-torres.md) | Generated from code |
```

---

# See Also

- `reference-persona.md` - Main persona reference
- `reference-philosophy.md#generate-mode` - Generate mode philosophy
- `help/persona.md` - Quick command help
- `templates/personas/persona-template.md` - Persona template

---

## Navigation {#navigation}

**Parent workflow:**

- `reference-persona.md` - Main persona workflows

**Source analysis:**

- `reference-prd.md` - Understanding PRD structure (for --from-prd)

**Downstream:**

- `reference-story.md` - Stories reference generated personas
