<!--
Load: On /sdlc-studio persona or /sdlc-studio persona help
Dependencies: SKILL.md (always loaded first)
Related: reference-persona.md, reference-persona-generate.md
-->

# /sdlc-studio persona - User Personas

## Quick Reference

```
/sdlc-studio persona                    # Ask which mode
/sdlc-studio persona create             # Interactive creation
/sdlc-studio persona generate           # Reverse engineer (see sources below)
/sdlc-studio persona import [file]      # Import existing markdown
/sdlc-studio persona list               # Show all project personas
/sdlc-studio persona export [name]      # Export persona for reuse
/sdlc-studio persona review             # Review and refine existing
```

## Persona Categories

Personas are organised into two categories:

| Category | Purpose | Examples |
|----------|---------|----------|
| **Team** | Internal team (Three Amigos) | PM, Developer, QA Lead |
| **Stakeholder** | External users and business | End User, Executive, Security |

### Three Amigos (Team)

| Amigo | Focus | Archetype Examples |
|-------|-------|-------------------|
| Product | What & Why | Sarah Chen (PM), Alex Rivera (BA) |
| Engineering | How | Marcus Johnson (Senior Dev), Nadia Okonkwo (Architect) |
| QA | What If | Priya Sharma (QA Lead), Jordan Lee (Automation) |

---

## Actions

### create

Interactive creation of rich, detailed personas.

**What happens:**
1. Choose category (Team or Stakeholder)
2. For Team: assign to amigo (Product/Engineering/QA)
3. Guided questions for identity, context, psychology
4. Option to start from archetype and customise
5. Writes individual file to `sdlc-studio/personas/`

**Options:**
- `--from-archetype [name]` - Start from an archetype persona

### generate

Reverse engineer personas from existing sources.

**Source options:**

| Flag | Source | Best For |
|------|--------|----------|
| `--from-prd [file]` | PRD document | Projects with requirements docs |
| `--from-code` | Codebase analysis | Brownfield projects with auth/roles |
| `--from-docs` | Documentation | Projects with user guides |

**What happens:**
1. **Discovery** - Analyse source for potential personas
2. **Presentation** - Show findings with evidence
3. **Enrichment** - Interactive questions to add depth
4. **Categorisation** - Assign to Team/Stakeholder
5. **Validation** - Check against archetypes, offer to customise
6. **Write** - Create individual persona files

**Depth options:**
- `--quick` - Minimal questions, fast creation
- `--thorough` - Full questionnaire, detailed personas

> **Deep dive:** `reference-persona-generate.md` - Full generate workflows

### import

Import an existing persona markdown file.

```
/sdlc-studio persona import ./existing-persona.md
```

**What happens:**
1. Reads and validates the file
2. Asks for category and type
3. Copies to project persona directory
4. Updates index

### list

Display all personas for current project.

```
/sdlc-studio persona list
```

**Output:**
```
TEAM PERSONAS

Product:
  Sarah Chen (PM) - Strategic decisions, scope control

Engineering:
  Marcus Johnson (Senior Dev) - Technical quality
  Chris Morgan (DevOps) - Operations, deployment

QA:
  Priya Sharma (QA Lead) - Test strategy

STAKEHOLDER PERSONAS

Users:
  Emma Wilson (Power User) - Efficiency, shortcuts
  Tom Bradley (Novice) - Onboarding, guidance

Business:
  James Mitchell (Exec) - ROI, timelines
```

### export

Export a persona for use in other projects.

```
/sdlc-studio persona export sarah-chen
```

Copies the persona file to a specified location or clipboard.

### review

Review and refine existing personas.

**What happens:**
1. Loads all persona files
2. For each: asks about updates needed
3. Asks if new personas needed
4. Updates files and index

---

## Output Structure

```
sdlc-studio/personas/
├── index.md                    # Persona index
├── team/
│   ├── product/
│   ├── engineering/
│   └── qa/
└── stakeholders/
    ├── users/
    ├── business/
    └── technical/
```

Each persona file includes:
- Quick reference table
- Identity and personality
- Professional context
- Psychology and decision drivers
- Interaction guide
- Backstory

---

## Examples

```bash
# Interactive creation
/sdlc-studio persona create

# Start from archetype
/sdlc-studio persona create --from-archetype sarah-chen-pm

# Generate from PRD
/sdlc-studio persona generate --from-prd sdlc-studio/prd.md

# Generate from codebase (brownfield project)
/sdlc-studio persona generate --from-code

# Quick generation (minimal questions)
/sdlc-studio persona generate --from-prd prd.md --quick

# Thorough generation (full detail)
/sdlc-studio persona generate --from-code --thorough

# Import existing persona
/sdlc-studio persona import ~/templates/security-officer.md

# List all personas
/sdlc-studio persona list

# Export for reuse
/sdlc-studio persona export marcus-johnson
```

---

## Archetypes Available

Pre-built personas in `templates/personas/`:

**Team - Product:**
- `sarah-chen-pm` - Product Manager
- `alex-rivera-ba` - Business Analyst

**Team - Engineering:**
- `marcus-johnson-senior-dev` - Senior Developer
- `kai-tanaka-junior-dev` - Junior Developer
- `nadia-okonkwo-architect` - Software Architect
- `chris-morgan-devops` - DevOps Engineer

**Team - QA:**
- `priya-sharma-qa-lead` - QA Lead
- `jordan-lee-automation` - Test Automation Engineer

**Stakeholders - Users:**
- `emma-wilson-power-user` - Power User
- `tom-bradley-novice` - Novice User
- `lisa-chen-accessibility` - Accessibility User

**Stakeholders - Business:**
- `james-mitchell-exec` - Executive Sponsor
- `diana-reyes-ops` - Operations Manager

**Stakeholders - Technical:**
- `david-park-security` - Security Lead
- `rachel-kim-compliance` - Compliance Officer

---

## Best Practices

- **Coverage:** Include at least one from each amigo for Team personas
- **Balance:** Mix Team and Stakeholder personas
- **Validation:** Use `--from-prd` or `--from-code` to ground personas in reality
- **Customisation:** Start from archetypes and adapt to your project
- **Reference:** Every User Story should name a persona

---

## Why Personas Matter

Personas are required for `/sdlc-studio story` generation. Each User Story starts with:
> **As a** {persona name}...

Personas enable:
- `/sdlc-studio consult` - Get feedback from persona perspective
- `/sdlc-studio chat` - Interactive conversations with personas

---

## Next Steps

After creating personas:
```
/sdlc-studio story          # Generate User Stories (requires personas)
/sdlc-studio consult        # Get persona feedback on artefacts (Phase 3)
```

---

## See Also

**Workflows:**
- `reference-persona.md` - Main persona reference
- `reference-persona-generate.md` - Generate workflow details
- `reference-philosophy.md#generate-mode` - Generate mode philosophy

**Related commands:**
- `/sdlc-studio prd help` - Product requirements (upstream)
- `/sdlc-studio story help` - User Stories (downstream)
- `/sdlc-studio consult help` - Persona consultation (Phase 3)
