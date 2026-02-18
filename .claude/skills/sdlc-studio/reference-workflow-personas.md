# SDLC Studio Reference - Workflow Persona Integration

How personas integrate across all SDLC Studio workflows.

<!-- Load when: Understanding persona integration patterns -->

---

# Overview

Personas can be consulted at key decision points throughout the SDLC pipeline. This reference describes when persona consultation adds value, when to skip it, and how to control integration behaviour.

---

# Integration Points

## Summary Table

| Workflow | Trigger | Default | Personas Consulted | Value |
|----------|---------|---------|-------------------|-------|
| PRD Create | After draft | Optional (prompt) | Team (Three Amigos) | HIGH |
| PRD Generate | After generation | Recommended | Team + relevant stakeholders | HIGH |
| PRD Review | If significant changes | Optional (prompt) | Team | MEDIUM |
| Epic Create | After generation | Optional (prompt) | Affected stakeholders | MEDIUM |
| Story Create | After AC defined | Optional (prompt) | Story persona + QA | HIGH |
| Story Review | On status change | Off | Story persona | LOW |
| Spec Review | Before implementation | Off | Engineering team | MEDIUM |
| Test Strategy | After TSD draft | Off | QA team | LOW |

---

# Flags

## Control Flags

| Flag | Effect | Available On |
|------|--------|--------------|
| `--with-personas` | Force persona consultation | All create/generate commands |
| `--skip-personas` | Skip persona consultation | All create/generate commands |
| `--persona [name]` | Consult specific persona only | All commands with persona integration |

## Depth Flags

| Flag | Effect | When to Use |
|------|--------|-------------|
| `--quick` | Brief feedback (1-2 sentences) | Draft reviews, iteration |
| `--thorough` | Detailed analysis | Final reviews, major decisions |

---

# Per-Workflow Integration

## PRD Workflows {#prd-integration}

### PRD Create

**When:** After step 6 (Write PRD)

**Default:** Prompt user - "Would you like Three Amigos review?"

**Rationale:** PRD is the foundation. Catching issues here is 10-100x cheaper than fixing later.

**Personas consulted:**
- Sarah Chen (PM) - Requirements completeness
- Marcus Johnson (Senior Dev) - Technical feasibility
- Priya Sharma (QA Lead) - Testability

**Integration:**
```bash
# With persona consultation (explicit)
/sdlc-studio prd create --with-personas

# Skip consultation
/sdlc-studio prd create --skip-personas

# Default: prompts after draft
/sdlc-studio prd create
```

### PRD Generate

**When:** After step 5 (Write PRD)

**Default:** Strongly recommend consultation

**Rationale:** Generated PRDs may have inferred requirements that need human validation. Personas catch assumptions.

**Personas consulted:**
- Team (Three Amigos) - Always
- Relevant stakeholders based on PRD content

### PRD Review

**When:** After step 5 (Report Changes) - only if significant changes found

**Default:** Prompt if changes found

**Triggers for consultation:**
- New features discovered
- Features marked as broken
- Scope changes identified

---

## Epic Workflows {#epic-integration}

### Epic Create

**When:** After step 6 (Report)

**Default:** Optional (prompt user)

**Rationale:** Epics define scope boundaries. Stakeholder input ensures nothing is missed.

**Personas consulted:**
- Personas mentioned in epic's "Affected Personas" section
- Business stakeholders for prioritisation input

**Integration:**
```bash
# Consult affected personas
/sdlc-studio epic --with-personas

# Skip consultation
/sdlc-studio epic --skip-personas

# Consult specific stakeholder
/sdlc-studio epic --persona james-mitchell
```

### Epic Review

**When:** During cascading review

**Default:** Off (too frequent)

**Enable with:** `--with-personas` flag

---

## Story Workflows {#story-integration}

### Story Create

**When:** After step 8 (Cohesion Review)

**Default:** Optional (prompt user)

**Rationale:** Story personas can validate that acceptance criteria match their actual needs.

**Personas consulted:**
- The persona in each story's "As a..." clause
- QA Lead for testability review

**Integration:**
```bash
# Validate all stories with their personas
/sdlc-studio story --with-personas

# Skip validation
/sdlc-studio story --skip-personas

# Validate specific story's persona only
/sdlc-studio story --story US0001 --with-personas
```

### Story Review

**When:** On status transitions

**Default:** Off

**Rationale:** Too frequent; would slow down development cycle.

**Enable selectively:**
```bash
/sdlc-studio consult emma-wilson sdlc-studio/stories/US0001.md
```

---

## Technical Workflows {#technical-integration}

### TRD Create/Generate

**When:** After TRD draft

**Default:** Off

**Rationale:** TRD is technical; most personas aren't relevant.

**Enable for:**
- Security Lead (David Park) - If security-sensitive
- DevOps (Chris Morgan) - If infrastructure changes

```bash
/sdlc-studio trd create --persona david-park
```

### Spec Review

**When:** Before implementation

**Default:** Off

**Enable for:**
- Engineering team review of complex designs

---

# Cost Considerations {#cost}

## When Consultation Adds Most Value

| Scenario | Value | Recommendation |
|----------|-------|----------------|
| New project PRD | HIGH | Always consult |
| Major scope change | HIGH | Consult team |
| User-facing feature | HIGH | Consult user personas |
| Internal tooling | LOW | Skip or quick mode |
| Bug fixes | LOW | Skip |
| Refactoring | LOW | Skip |

## Cost Reduction Strategies

1. **Use `--quick` for iterations**
   - Full consultation on final review only
   - Quick mode during drafts

2. **Use `--relevant` to auto-filter**
   - Only consults personas relevant to artefact
   - Reduces token usage

3. **Batch consultations**
   - Consult once after generating multiple stories
   - Rather than per-story

4. **Skip for low-risk changes**
   - Documentation updates
   - Minor bug fixes
   - Internal refactoring

---

# Automatic vs Manual Consultation

## Automatic (Built into Workflow)

Workflows prompt for consultation at appropriate points:

```
PRD draft complete.

Would you like Three Amigos review of this PRD?
  [Yes] - Run /sdlc-studio consult team prd.md
  [No] - Skip persona consultation
  [Later] - I'll run it manually when ready
```

## Manual (User-Initiated)

User can run consultation at any time:

```bash
# Consult any persona on any artefact
/sdlc-studio consult sarah-chen sdlc-studio/prd.md

# Team review
/sdlc-studio consult team sdlc-studio/epics/EP0001.md

# All stakeholders
/sdlc-studio consult stakeholders sdlc-studio/prd.md
```

---

# Persona Relevance Mapping

## Which Personas for Which Artefacts

| Artefact Type | Primary Personas | Secondary Personas |
|---------------|------------------|-------------------|
| PRD | PM, End Users | Executive, Security |
| TRD | Senior Dev, Architect | DevOps, Security |
| Epic | PM, Affected Users | Engineering Lead |
| Story | Story Persona | QA Lead |
| Test Strategy | QA Lead, QA Team | Senior Dev |
| Technical Spec | Engineering Team | Security, Compliance |

## Auto-Selection Logic

When using `--relevant` or automatic consultation:

1. **Artefact type mapping** (above table)
2. **Content analysis** - Personas mentioned in artefact
3. **Domain matching** - Persona expertise vs artefact domain
4. **Historical utility** - Previously useful feedback

---

# Configuration

## Project-Level Defaults

In `sdlc-studio/config.yaml`:

```yaml
personas:
  # Default consultation behaviour
  consult_on_prd: prompt      # always, prompt, never
  consult_on_epic: prompt
  consult_on_story: prompt

  # Default depth
  default_depth: standard     # quick, standard, thorough

  # Auto-filter by relevance
  auto_relevant: true

  # Minimum relevance score (0-100)
  relevance_threshold: 30
```

## Per-Command Override

Flags override project defaults:

```bash
# Override to always consult
/sdlc-studio prd create --with-personas

# Override to skip
/sdlc-studio story --skip-personas
```

---

# See Also

- `reference-consult.md` - Consultation command details
- `reference-persona.md` - Persona management
- `reference-prd.md` - PRD workflow with persona integration
- `reference-epic.md` - Epic workflow with persona integration
- `reference-story.md` - Story workflow with persona integration

---

## Navigation

**Integration details:**
- `reference-prd.md#prd-create-workflow` - Step 7: Persona Consultation
- `reference-epic.md#epic-workflow` - Step 7: Affected Personas Assessment
- `reference-story.md#story-workflow` - Step 9: Persona Validation
