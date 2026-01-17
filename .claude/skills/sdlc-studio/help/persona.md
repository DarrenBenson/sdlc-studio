# /sdlc-studio persona - User Personas

## Quick Reference

```
/sdlc-studio persona                # Interactive creation
/sdlc-studio persona generate       # Infer from codebase
/sdlc-studio persona update         # Refine existing
```

## Actions

### create (default)
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

### update
Refine existing personas with new information.

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

# Update existing personas
/sdlc-studio persona update
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

- `/sdlc-studio story help` - Generate Stories (requires personas)
- `/sdlc-studio prd help` - PRD often informs persona creation
