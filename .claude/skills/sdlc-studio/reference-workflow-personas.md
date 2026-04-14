# SDLC Studio Reference - Workflow Persona Integration

How personas integrate across all SDLC Studio workflows.

<!-- Load when: Understanding persona integration patterns -->

---

## Overview

Personas can be consulted at key decision points throughout the SDLC pipeline. This reference describes when persona consultation adds value, when to skip it, and how to control integration behaviour.

---

## Integration Points

## Summary Table

| Workflow | Trigger | Default | Personas Consulted | Value |
| --- | --- | --- | --- | --- |
| PRD Create | After draft | Optional (prompt) | Team (Three Amigos) | HIGH |
| PRD Generate | After generation | Recommended | Team + relevant stakeholders | HIGH |
| PRD Review | If significant changes | Optional (prompt) | Team | MEDIUM |
| Epic Create | After generation | **Always** | Three Amigos + affected stakeholders | HIGH |
| Story Create | After AC defined | **Always** | Three Amigos (PM: completeness, Eng: TRD alignment, QA: testability) | HIGH |
| Story Plan | After plan created | **Always** | Three Amigos (PM: scope, Eng: approach, QA: test strategy) | HIGH |
| Story Review | On status change | Optional (prompt) | Three Amigos | MEDIUM |
| Bug Fix | After root cause analysis | **Always** | Three Amigos (PM: impact, Eng: root cause, QA: regression) | HIGH |
| Bug Verify | After fix complete | Optional (prompt) | QA Lead | MEDIUM |
| Spec Review | Before implementation | Off | Engineering team | MEDIUM |
| Test Strategy | After TSD draft | Off | QA team | LOW |

---

## Flags

## Control Flags

| Flag | Effect | Available On |
| --- | --- | --- |
| `--with-personas` | Force persona consultation | All create/generate commands |
| `--skip-personas` | Skip persona consultation | All create/generate commands |
| `--persona [name]` | Consult specific persona only | All commands with persona integration |

## Depth Flags

| Flag | Effect | When to Use |
| --- | --- | --- |
| `--quick` | Brief feedback (1-2 sentences) | Draft reviews, iteration |
| `--thorough` | Detailed analysis | Final reviews, major decisions |

---

## Per-Workflow Integration

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

**Default:** Always (Three Amigos)

**Rationale:** Epics define scope boundaries and technical approach. Three Amigos ensure requirements completeness (PM), technical feasibility (Eng), and testability (QA). Affected stakeholder personas provide additional domain-specific feedback.

**Personas consulted:**

- **Sarah Chen (PM):** Validates scope, success metrics, user value, and feature boundaries
- **Marcus Johnson (Eng):** Reviews TRD alignment, architecture impact, dependency graph, and technical risks
- **Priya Sharma (QA):** Assesses testability, edge case coverage, TSD alignment, and quality gates
- Personas mentioned in epic's "Affected Personas" section (additional)

**Integration:**

```bash
# Default: Three Amigos consultation runs automatically
/sdlc-studio epic

# Skip consultation
/sdlc-studio epic --skip-personas

# Consult specific stakeholder in addition to Three Amigos
/sdlc-studio epic --persona david-park
```

### Epic Review

**When:** During cascading review

**Default:** Optional (prompt) - Three Amigos when enabled

**Enable with:** `--with-personas` flag

---

## Story Workflows {#story-integration}

### Story Create

**When:** After step 8 (Cohesion Review)

**Default:** Always (Three Amigos)

**Rationale:** Stories define the implementation contract. Three Amigos ensure completeness (PM), technical alignment (Eng), and testability (QA). Each amigo reviews from their professional perspective against the relevant source documents.

**Personas consulted:**

- **Sarah Chen (PM):** Validates user value, AC completeness, persona alignment, and that the story addresses the right user problem
- **Marcus Johnson (Eng):** Reviews TRD alignment, technical notes accuracy, dependency correctness, and that implementation guidance is feasible
- **Priya Sharma (QA):** Assesses AC testability, edge case completeness, TSD alignment, and that test scenarios cover the risk profile

**Integration:**

```bash
# Default: Three Amigos consultation runs automatically
/sdlc-studio story

# Skip consultation
/sdlc-studio story --skip-personas

# Validate specific story only
/sdlc-studio story --story US0001 --with-personas
```

### Story Plan

**When:** After plan creation (code plan)

**Default:** Always (Three Amigos)

**Rationale:** Plans define the implementation approach. Three Amigos ensure the approach is sound before coding begins.

**Personas consulted:**

- **Sarah Chen (PM):** Validates scope alignment, that plan addresses all ACs, and no scope creep
- **Marcus Johnson (Eng):** Reviews implementation approach, architecture alignment, edge case handling plan
- **Priya Sharma (QA):** Validates test strategy recommendation (TDD vs Test-After), test coverage plan

**Integration:**

```bash
# Default: Three Amigos review runs automatically after plan creation
/sdlc-studio code plan --story US0001

# Skip consultation
/sdlc-studio code plan --story US0001 --skip-personas
```

### Story Review

**When:** On status transitions

**Default:** Optional (prompt) - Three Amigos when enabled

**Rationale:** Useful for significant transitions (Ready, Review, Done) but too frequent for every status change.

**Enable selectively:**

```bash
# Three Amigos review of a specific story
/sdlc-studio consult team sdlc-studio/stories/US0001.md

# Single persona review
/sdlc-studio consult priya-sharma sdlc-studio/stories/US0001.md
```

### Bug Fix

**When:** After root cause analysis (bug fix step 4)

**Default:** Always (Three Amigos)

**Rationale:** Bug fixes need multi-perspective review: user impact assessment (PM), root cause validation and fix approach review (Eng), and regression test planning (QA).

**Personas consulted:**

- **Sarah Chen (PM):** Assesses user impact, validates fix priority against roadmap
- **Marcus Johnson (Eng):** Reviews root cause analysis, validates fix approach, checks for architectural implications
- **Priya Sharma (QA):** Plans regression tests, identifies related test scenarios, assesses risk of fix introducing new issues

**Integration:**

```bash
# Default: Three Amigos consultation runs after root cause analysis
/sdlc-studio bug fix --bug BG0001

# Skip consultation
/sdlc-studio bug fix --bug BG0001 --skip-personas
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

## Cost Considerations {#cost}

## When Consultation Adds Most Value

| Scenario | Value | Recommendation |
| --- | --- | --- |
| New project PRD | HIGH | Always consult (Three Amigos) |
| Major scope change | HIGH | Consult team (Three Amigos) |
| User-facing feature | HIGH | Consult user personas + Three Amigos |
| Epic creation | HIGH | Always consult (Three Amigos + stakeholders) |
| Story creation | HIGH | Always consult (Three Amigos) |
| Story planning | HIGH | Always consult (Three Amigos) |
| Bug fixes | HIGH | Always consult (Three Amigos: impact, root cause, regression) |
| Internal tooling | MEDIUM | Three Amigos (quick mode) |
| Refactoring | LOW | Skip or quick mode |

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

## Automatic vs Manual Consultation

## Automatic (Built into Workflow)

Workflows prompt for consultation at appropriate points:

```text
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

## Persona Relevance Mapping

## Which Personas for Which Artefacts

| Artefact Type | Primary Personas | Secondary Personas |
| --- | --- | --- |
| PRD | PM, End Users | Executive, Security |
| TRD | Senior Dev, Architect | DevOps, Security |
| Epic | Three Amigos (PM, Eng, QA) | Affected stakeholders |
| Story | Three Amigos (PM, Eng, QA) | Story persona |
| Plan | Three Amigos (PM, Eng, QA) | - |
| Bug | Three Amigos (PM, Eng, QA) | Affected story persona |
| Test Strategy | QA Lead, QA Team | Senior Dev |
| Technical Spec | Engineering Team | Security, Compliance |

## Auto-Selection Logic

When using `--relevant` or automatic consultation:

1. **Artefact type mapping** (above table)
2. **Content analysis** - Personas mentioned in artefact
3. **Domain matching** - Persona expertise vs artefact domain
4. **Historical utility** - Previously useful feedback

---

## Configuration

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

## See Also

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
