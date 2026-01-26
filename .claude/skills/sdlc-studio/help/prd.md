<!--
Load: On /sdlc-studio prd or /sdlc-studio prd help
Dependencies: SKILL.md (always loaded first)
Related: reference-prd.md (deep workflow), templates/prd-template.md
-->

# /sdlc-studio prd - Product Requirements Document

## Quick Reference

```
/sdlc-studio prd                    # Ask which mode
/sdlc-studio prd create             # Interactive creation
/sdlc-studio prd generate           # Reverse-engineer from codebase
/sdlc-studio prd review             # Review PRD against codebase
```

## Actions

### create
Interactive conversation to build a PRD from scratch.

**What happens:**
1. Claude asks about project name, purpose, target users
2. You describe features one by one with acceptance criteria
3. Claude asks about non-functional requirements (performance, security)
4. PRD is written to `sdlc-studio/prd.md`

**Best for:** New projects, greenfield development

### generate
Analyse existing codebase and reverse-engineer requirements.

**What happens:**
1. Claude explores your codebase (routes, components, tests, config)
2. Extracts features and infers acceptance criteria
3. Documents technical architecture found
4. PRD is written with confidence markers ([HIGH], [MEDIUM], [LOW])

> **New to generate mode?** Read `reference-philosophy.md#generate-mode` first - it explains why generated specs must be validated by tests.

**Best for:** Existing projects needing documentation

### review
Review PRD against current codebase, update feature status.

**What happens:**
1. Reads existing PRD from `sdlc-studio/prd.md`
2. Searches codebase for each feature's implementation
3. Updates status: Complete | Partial | Stubbed | Broken | Not Started
4. Discovers new features not in PRD

**Best for:** Tracking progress, keeping docs current

## Output

**File:** `sdlc-studio/prd.md`

**Sections:**
1. Project Overview
2. Problem Statement
3. Feature Inventory
4. Functional Requirements
5. Non-Functional Requirements
6. AI/ML Specifications (if applicable)
7. Data Architecture
8. Integration Map
9. Configuration Reference
10. Test Coverage Analysis
11. Technical Debt Register
12. Documentation Gaps
13. Recommendations
14. Open Questions

## Examples

```
# Start fresh project
/sdlc-studio prd create

# Document existing codebase
/sdlc-studio prd generate

# Review status after sprint
/sdlc-studio prd review

# Overwrite existing PRD
/sdlc-studio prd generate --force
```

## Next Steps

After creating PRD:
```
/sdlc-studio persona              # Define user personas
/sdlc-studio epic                 # Generate Epics from PRD
```

## See Also

**REQUIRED for this workflow:**
- `reference-philosophy.md#generate-mode` - Understand specification extraction (generate mode only)
- `reference-prd.md` - PRD workflow details

**Recommended:**
- `/sdlc-studio epic help` - Generate Epics from PRD (downstream)
- `/sdlc-studio trd help` - Technical requirements (parallel)

**Optional (deep dives):**
- `reference-outputs.md` - Output formats reference
