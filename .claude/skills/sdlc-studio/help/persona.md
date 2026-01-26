<!--
Load: On /sdlc-studio persona or /sdlc-studio persona help
Dependencies: SKILL.md (always loaded first)
Related: reference-persona.md (deep workflow), templates/personas-template.md
-->

# /sdlc-studio persona - User Personas

## Quick Reference

```
/sdlc-studio persona                # Ask which mode (create/generate/review)
/sdlc-studio persona create         # Interactive creation
/sdlc-studio persona generate       # Infer from codebase
/sdlc-studio persona review         # Review and refine existing
```

## Actions

### (default)
Ask which mode to use.

**What happens:**
1. Prompts for mode selection:
   - **Create** - Start from scratch with guided questions
   - **Generate** - Infer personas from codebase patterns
   - **Review** - Review and update existing personas

### create
Interactive conversation to define user personas.

**What happens:**
1. Claude guides you through persona creation
2. For each persona: name, role, goals, pain points, typical tasks
3. Recommends 3-5 personas per project
4. Writes to `sdlc-studio/personas.md`

**Questions asked:**
- Persona name (memorable, humanising)
- Role/job title
- Technical proficiency level
- Primary goal
- Background (2-3 sentences)
- Key needs (3-5 items)
- Pain points (3-5 items)
- Typical tasks (3-5 items)
- Representative quote

### generate
Analyse codebase to infer user types.

**What happens:**
1. Searches for role/permission definitions
2. Analyses authentication/authorisation patterns
3. Identifies UI journeys for different users
4. Finds user type mentions in docs/comments
5. Drafts personas with [INFERRED] markers
6. Asks for validation before writing

**Best for:** Existing projects with role-based access

### review
Review and refine existing personas with new information.

**What happens:**
1. Loads existing `sdlc-studio/personas.md`
2. For each persona, asks about changes
3. Asks if new personas needed
4. Updates file with revision history

## Output

**File:** `sdlc-studio/personas.md`

**Persona structure:**
```markdown
## {Persona Name}

**Role:** {job title}
**Technical Proficiency:** Novice | Intermediate | Advanced | Expert
**Primary Goal:** {one sentence}

### Background
{2-3 sentences}

### Needs & Motivations
- {need 1}
- {need 2}

### Pain Points
- {pain point 1}
- {pain point 2}

### Typical Tasks
- {task 1}
- {task 2}

### Quote
> "{representative quote}"
```

## Examples

```
# Interactive persona creation
/sdlc-studio persona

# Infer from codebase
/sdlc-studio persona generate

# Review and refine existing personas
/sdlc-studio persona review
```

## Best Practices

- **3-5 personas** per project (too few misses perspectives, too many dilutes focus)
- **Memorable names** help team discussions ("Would Power User Pat need this?")
- **Validate with research** - interview actual users if possible
- **Reference in stories** - every User Story should name a persona

## Why Personas Matter

Personas are required for `/sdlc-studio story` generation. Each User Story starts with:
> **As a** {persona name}...

Without personas, Stories become generic and lose user focus.

## Next Steps

After creating Personas:
```
/sdlc-studio story                # Generate User Stories (requires personas)
```

## See Also

**REQUIRED for this workflow:**
- `reference-philosophy.md#generate-mode` - Understand specification extraction (generate mode only)
- `reference-persona.md` - Persona workflow details

**Recommended:**
- `/sdlc-studio prd help` - Product requirements (upstream)
- `/sdlc-studio story help` - User Stories (downstream)

**Optional (deep dives):**
- `reference-outputs.md` - Output formats reference
