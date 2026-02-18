<!--
Load: On /sdlc-studio consult or /sdlc-studio consult help
Dependencies: SKILL.md (always loaded first)
Related: reference-consult.md, reference-persona.md
-->

# /sdlc-studio consult - Persona Consultation

> **Source of truth:** `reference-consult.md` - Detailed workflow steps

Get structured feedback from personas on SDLC artefacts.

## Quick Reference

```bash
/sdlc-studio consult [persona] [artefact]     # Single persona feedback
/sdlc-studio consult team [artefact]          # Three Amigos review
/sdlc-studio consult stakeholders [artefact]  # All stakeholder personas
/sdlc-studio consult all [artefact]           # Everyone
```

## How It Works

1. Claude loads the persona's full profile (goals, concerns, decision style)
2. Reviews the artefact "in character" as that persona
3. Returns structured feedback with verdict, questions, and conditions

**Key Difference from `/sdlc-studio chat`:**
- `consult` = Automated, structured output, no back-and-forth
- `chat` = Interactive conversation, follow-up questions

---

## Actions

### Single Persona

```bash
/sdlc-studio consult sarah-chen sdlc-studio/prd.md
```

Get feedback from one specific persona.

**Output:**
```markdown
## Sarah Chen (Product Manager)
**Verdict:** ⚠️ Concerns

"The problem statement is solid, but I'm not seeing clear
success metrics. How will we measure if this feature is working?"

**Questions:**
- What's our baseline for current user behaviour?
- Have we validated this with user research?

**Conditions for approval:**
- Add measurable success criteria
```

### Team (Three Amigos)

```bash
/sdlc-studio consult team sdlc-studio/prd.md
```

Get feedback from Product, Engineering, and QA perspectives.

**Default representatives:**
- Product: First Product persona or Sarah Chen
- Engineering: First Senior Engineer or Marcus Johnson
- QA: First QA persona or Priya Sharma

**Override defaults:**
```bash
/sdlc-studio consult team prd.md --engineering nadia-okonkwo
```

### Stakeholders

```bash
/sdlc-studio consult stakeholders sdlc-studio/prd.md
```

Get feedback from all stakeholder personas (Users, Business, Technical).

### All

```bash
/sdlc-studio consult all sdlc-studio/prd.md
```

Get feedback from Team AND Stakeholders. Most comprehensive but highest cost.

---

## Options

### Depth Control

| Flag | Feedback Length | Questions |
|------|-----------------|-----------|
| `--quick` | 1-2 sentences | 1-2 |
| (default) | 2-4 sentences | 2-4 |
| `--thorough` | Full analysis | 4-6 |

### Filtering

```bash
# Only relevant personas (auto-filtered by artefact type)
/sdlc-studio consult stakeholders prd.md --relevant

# Exclude specific persona
/sdlc-studio consult all prd.md --exclude james-mitchell
```

### Output

```bash
# Write to file
/sdlc-studio consult team prd.md --output reviews/prd-review.md

# Append to artefact as review section
/sdlc-studio consult team prd.md --append

# JSON format (for automation)
/sdlc-studio consult team prd.md --format json
```

---

## Verdict Types

| Verdict | Meaning | Action |
|---------|---------|--------|
| ✅ Approve | Ready to proceed | Continue to next step |
| ⚠️ Concerns | Can proceed with conditions | Address conditions, then proceed |
| ❌ Reject | Cannot proceed | Must address before continuing |

---

## Examples

```bash
# Quick PRD review from PM
/sdlc-studio consult sarah-chen sdlc-studio/prd.md --quick

# Thorough Three Amigos review
/sdlc-studio consult team sdlc-studio/prd.md --thorough

# Story review by the persona mentioned in "As a..."
/sdlc-studio consult emma-wilson sdlc-studio/stories/US0001.md

# Security review of technical spec
/sdlc-studio consult david-park sdlc-studio/specs/auth-spec.md

# Full stakeholder review, save to file
/sdlc-studio consult stakeholders prd.md --output reviews/stakeholder-review.md

# Team review with custom Engineering representative
/sdlc-studio consult team prd.md --engineering nadia-okonkwo

# All personas, but only those relevant to the artefact
/sdlc-studio consult all prd.md --relevant
```

---

## Recommended Usage

### By Artefact Type

| Artefact | Recommended Command |
|----------|---------------------|
| PRD | `consult team` + `consult stakeholders --relevant` |
| Epic | `consult team` |
| Story | `consult [story-persona]` + QA |
| Technical Spec | `consult team --engineering nadia-okonkwo` |
| Test Strategy | `consult team` |

### By Project Phase

| Phase | Consultation |
|-------|--------------|
| Requirements | Team + Business stakeholders |
| Design | Team (especially Engineering) |
| Implementation | Story persona + QA |
| Pre-release | All stakeholders |

---

## Cost Considerations

| Command | Relative Cost | When to Use |
|---------|---------------|-------------|
| Single persona | Low | Targeted feedback |
| Team | Medium | Most decisions |
| Stakeholders | Medium-High | User-facing changes |
| All | High | Major decisions, releases |

**Tips:**
- Use `--quick` for draft reviews
- Use `--thorough` for final reviews
- Use `--relevant` to auto-filter stakeholders

---

## Prerequisites

Personas must exist in `sdlc-studio/personas/`. If not:

```bash
/sdlc-studio persona create    # Create interactively
/sdlc-studio persona generate  # Generate from PRD/code
```

---

## Next Steps

After consultation:

- Address concerns raised by personas
- Re-consult if significant changes made
- Proceed to next pipeline step when approved

For interactive follow-up questions:
```bash
/sdlc-studio chat [persona]    # Phase 5
```

---

## See Also

**Workflows:**
- `reference-consult.md` - Detailed consultation workflows
- `reference-persona.md` - Persona management

**Related commands:**
- `/sdlc-studio persona help` - Persona creation
- `/sdlc-studio chat help` - Interactive sessions (Phase 5)
- `/sdlc-studio review help` - Document review workflows
