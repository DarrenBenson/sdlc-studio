# SDLC Studio Reference - Consult

Detailed workflows for persona consultation on SDLC artefacts.

<!-- Load when: /sdlc-studio consult is invoked -->

---

## Overview

The consult command gets structured feedback from personas on SDLC artefacts. Unlike `/sdlc-studio chat` (interactive), consult is automated and returns structured output.

**Key Principle:** Each seat reviews against a structured **charter** (role, lens, non-negotiables,
shadow), and is consulted as an **isolated subagent** (its own fresh context) so its view is
genuinely independent, not a hat worn in the main thread. Verdicts land in the existing ledgers
(`critic.py` / `ledger.py`) - the record lives outside the seat, the stance inside it.

**Resolve the seat through the declared-`role:` chain - the same resolver delegation uses, not the
template name or H1 prose.** A consult must run from the project's authored seat when one fills the
role, exactly as `persona_resolve` frames a delegated worker:

1. a project review seat in `sdlc-studio/personas/seats/` whose declared `<!-- role: ... -->` field
   matches the seat (named after a person, matched on the field, never the filename or H1 prose);
   then
2. the skill default seat (`templates/personas/amigos/<seat>.md`); then
3. the generic enriched seat schema (`templates/personas/amigo-template.md`) as the fallback when no
   seat fills the role.

Resolve the **review render** of the matched seat (a consult critiques). A seat present but missing
its review render is a **hard error**, never a silent fallback to the generic schema.
Use `persona_resolve.py resolve-consult --role <role> --root <root>` to pick the card by declared
role and surface the render-less error - it reuses the delegation resolver, so consult and
delegation honour the same authored seat.

**Two disciplines apply to every consult, whatever the mode:**

- **The Primary test (arbitration).** For any feature-shaped question, each seat asks:
  does this serve the Primary persona's End Goals? If not, cut or demote it - a
  stakeholder's want is met elsewhere, never by bending the Primary's interface.
- **The objection quota (anti-sycophancy).** Every consulted seat raises at least one
  concrete objection or states why none exists. A panel of favourable-and-vague verdicts
  is a failed consult, not a passed one - the output templates carry an
  `Objection (or why none)` field per seat so the quota is visible, and the eval suite
  grades it.

---

## Consultation Modes

## Single Persona {#single-persona}

```bash
/sdlc-studio consult [persona-name] [artefact]
```

Get feedback from one specific persona.

**Example:**

```bash
/sdlc-studio consult sarah-chen sdlc-studio/prd.md
/sdlc-studio consult marcus-johnson sdlc-studio/stories/US0001.md
```

### Workflow

1. **Resolve the Seat Charter** (declared-`role:` chain - see the Key Principle above)
   - Resolve the card through the chain: a project `personas/seats/` card whose declared role
     matches, else the skill default seat, else the generic enriched seat schema
     (`templates/personas/amigo-template.md`) - via
     `persona_resolve.py resolve-consult --role <role> --root <root>`. When no authored seat exists
     and no default fits, generate one from an archetype seed (`reference-persona.md#archetypes`)
   - Use the matched seat's **review render**; a render-less seat is a hard error
   - Extract: role & mandate, lens, non-negotiables, pushes-back-when, shadow, authority, reads

2. **Load Artefact**
   - Read the specified artefact
   - Identify artefact type (PRD, Epic, Story, Spec, etc.)

3. **Generate Review Prompt** (run as an isolated subagent - fresh context)

   ```text
   You are the {{seat_name}} review seat ({{role}}).

   Your charter:
   - Mandate: {{mandate}}
   - Lens (your standing questions): {{lens}}
   - Non-negotiables: {{non_negotiables}}
   - You push back when: {{pushes_back_when}}
   - Your shadow, guard against it: {{shadow}}
   - Authority: approves {{approves}}; blocks {{blocks}}
   - You read: {{reads}}

   Review this {{artefact_type}} against your charter. Hold your stance under pressure - do not
   default to agreement to keep the peace (watch your shadow).

   Provide:
   1. Your verdict: ✅ Approve / ⚠️ Concerns / ❌ Reject
   2. Feedback in your voice (2-4 sentences)
   3. The questions your lens raises (2-4)
   4. Conditions for approval (if concerns or reject)
   ```

4. **Generate Feedback**
   - The subagent responds as the seat, holding the charter's stance

5. **Record + Format Output**
   - Record the verdict via `critic.py` / `ledger.py` (the externalised record)
   - Use the consultation output template; write to stdout or a file if `--output` specified

---

## Team Review (Three Amigos) {#team-review}

```bash
/sdlc-studio consult team [artefact]
```

Get feedback from one representative of each amigo.

### Default Team Selection

| Amigo | Default Persona | Rationale |
| --- | --- | --- |
| Product | First Product persona (or Sarah Chen) | Requirements perspective |
| Engineering | First Senior-level Engineering persona (or Marcus Johnson) | Technical perspective |
| QA | First QA persona (or Priya Sharma) | Quality perspective |

Override with `--product`, `--engineering`, `--qa` flags.

### Workflow

1. **Select Representatives**
   - Load project personas from `sdlc-studio/personas/index.md`
   - Select one from each amigo (or use defaults)

2. **Isolated Consultation** (one subagent per seat)
   - Run each seat as an **independent subagent in its own fresh context** - never as sequential
     hats in the main thread (a shared context contaminates the views; independence is the point)
   - Each reviews from its charter (Single-Persona workflow above)

3. **Synthesis** (a distinct step, after all seats return)
   - Merge the independent verdicts into the Three Amigos format: a summary table, then
     **consensus** (where seats agree) and **conflicts** (where they do not - name the tension and
     surface both sides for the operator to adjudicate rather than auto-resolving)
   - Record the synthesised verdict via `critic.py` / `ledger.py`

4. **Format Output**
   - Use team review template
   - Include recommended actions

### Example Output

```markdown
## Three Amigos Review: User Authentication PRD

### Product Perspective - Sarah Chen (PO)
**Verdict:** ⚠️ Concerns

"The scope is reasonable, but I'm not seeing success metrics..."

**Questions:**
- What's our target adoption rate?
- Have we validated with user research?

---

### Engineering Perspective - Marcus Johnson (Senior Dev)
**Verdict:** ✅ Approve with notes

"Architecture is solid. OAuth 2.0 is the right choice..."

**Questions:**
- Session timeout strategy?
- Refresh token rotation policy?

---

### QA Perspective - Priya Sharma (QA Lead)
**Verdict:** ⚠️ Concerns

"Testing SSO requires environment setup..."

**Questions:**
- Test accounts for each provider?
- Fallback testing strategy?

---

### Summary

| Amigo | Verdict | Key Concern |
|-------|---------|-------------|
| Product | ⚠️ | Missing success metrics |
| Engineering | ✅ | Session timeout clarity |
| QA | ⚠️ | Test environment needs |

**Consensus:** 1 approve, 2 concerns
**Recommendation:** Address concerns before proceeding

**Actions Required:**
1. Add success metrics to PRD
2. Document session timeout policy
3. Specify test environment requirements
```

---

## Stakeholder Review {#stakeholder-review}

```bash
/sdlc-studio consult stakeholders [artefact]
```

Get feedback from all stakeholder personas (not team).

### Workflow

1. **Load Stakeholder Personas**
   - Read all personas from `sdlc-studio/personas/stakeholders/`
   - Group by the declared `<!-- stakeholder: ... -->` type (buyer, compliance, ops,
     served); legacy cards without one group as Users, Business, Technical
   - Check provenance: `scripts/persona_gen.py classify --root .` - any card still
     `generated-pristine` is provisional-unverified and MUST be named in the output
     header (its feedback is an assumption, not research)
   - Apply each card's arbitration line: a buyer/Customer verdict never overrides the
     Primary persona's interface - record the conflict, route the need elsewhere

2. **Filter by Relevance** (optional with `--relevant`)
   - Score each persona's relevance to artefact
   - Skip personas with low relevance scores

3. **Parallel Consultation**
   - Run consultations for all selected personas

4. **Synthesise Results**
   - Group feedback by stakeholder type
   - Identify patterns across groups
   - Highlight conflicts between groups

### Example Output

One section per declared type present on the panel (Buyer, Compliance, Ops, Served);
legacy cards without a type group as Users, Business, Technical. Never render an
empty section.

```markdown
## Stakeholder Review: Feature X PRD

**Provisional (unverified) cards:** priya-nair.md

### Buyer Perspectives

#### James Mitchell (VP Operations, economic buyer)
**Verdict:** ✅ Approve
"ROI projections are solid. Timeline is aggressive but achievable."
**Objection (or why none):** none - the phased rollout answers my budget-cycle risk.

---

### Compliance Perspectives

#### Priya Nair (DPO)
**Verdict:** ⚠️ Concerns
"Data export feature needs access controls..."
**Objection (or why none):** export lacks an audit trail - veto line until logged.

---

### Served Perspectives

#### Emma Wilson (Warehouse picker - affected, never a user)
**Verdict:** ⚠️ Concerns
"Re-slotting driven by this system changes my pick routes mid-shift."
**Objection (or why none):** no notice period for route changes.

---

### Cross-Group Analysis

**Consensus Points:**
- Value proposition is clear
- Core functionality approved

**Conflicts:**
- Power users want advanced features vs Novices want simplicity
- Speed vs Security trade-offs identified

**Recommendations:**
1. Add progressive disclosure for complex features
2. Implement role-based access for data export
```

---

## All Personas {#all-personas}

```bash
/sdlc-studio consult all [artefact]
```

Get feedback from both Team and Stakeholder personas.

### Workflow

1. Run Team Review workflow
2. Run Stakeholder Review workflow
3. Combine results with clear separation
4. Generate unified summary

**Cost Note:** This is the most expensive option. Use `--quick` for abbreviated feedback or `--relevant` to filter personas.

---

## Multi-Persona Pressure-Test Canvas {#pressure-test-canvas}

When the design space is unsettled and the operator has multiple plausible options, a single-persona consult is the wrong tool – the persona will pick *one* of the options and argue for it, but the operator already has multiple voices in their head and needs to know which one converges. Use a **pressure-test canvas** instead.

### When to trigger

| Signal | Why |
| --- | --- |
| The operator says "I'm not sure if A or B is right" or "what's the cleanest way to..." | Genuine design uncertainty |
| The artefact has more than one option section / open-question section | Author already flagged the unsettledness |
| The first persona consulted offers a counter-offer instead of a ratification | The proposal is shaped wrong, not just imperfect |
| The decision has high blast-radius (architecture, migration, public API, schema change) | Cost of getting it wrong is high enough to warrant the parallel consult |

### How to conduct

1. **Identify the canvas members.** Pick personas that bring **different perspectives** (engineering, product, ops, security, customer-experience). Three personas is the minimum that gives convergent signal; five is the comfort point; more than seven adds noise without adding signal.
2. **Frame the proposal as a *single, complete* artefact** before sending to anyone. Half-formed proposals get half-formed feedback. State assumptions, options considered, and the proposed choice.
3. **Send to each canvas member in parallel** (in practice: sequential consults issued in one batch, results collected before synthesis).
4. **Each persona answers in their own voice.** Don't pre-bias by asking "do you agree?" – ask "what would you do, and why?"
5. **Synthesise.** Read the *Synthesis discipline* below.

### Synthesis discipline

The point of the canvas is **convergence**, not vote-counting. A 3-of-5 majority for A is not a decision; it is a sign that A might be defensible. A counter-offer that *all five* personas converge on, even if not literally articulated by any of them in those words, is a decision.

| Synthesis pattern | Meaning | Action |
| --- | --- | --- |
| All personas ratify the proposal | Proposal is correct | Ship it |
| All personas reject with **the same alternative** | Proposal is wrong; the alternative is right | Ship the alternative |
| All personas reject with **different alternatives** | Design space is more unsettled than thought | Reframe the proposal; canvas again |
| Personas split on the proposal but agree on *constraints the proposal violates* | The constraints, not the proposal, are the decision | Articulate the constraints; rewrite the proposal to satisfy them; canvas the rewrite |
| Some personas ratify, some reject without an alternative | Inconclusive; the rejecting personas have not engaged | Re-prompt the rejectors with the specific objection |

**Counter-offers more often than ratifications.** A canvas where 5/5 personas ratify the original proposal is suspicious – either the proposal is genuinely settled (in which case the canvas was unnecessary), or the personas weren't pressure-testing. If you keep getting unanimous ratifications, your canvas is rubber-stamping; widen the persona set.

### Canvas size

| Project type | Canvas |
| --- | --- |
| Solo-dev with persona files | 3 stakeholder personas |
| Team project | Three Amigos + 1–2 stakeholder personas (5 total) |
| Project with live agents | 3+ stakeholder personas plus available live agents (live agents amplify the canvas – different stack, different prior, more divergent feedback) |
| Greenfield with no personas yet | Skip the canvas; this is the wrong tool. Run a Three Amigos consult instead and create stakeholder personas as the design firms up |

**Live-agent amplification:** Projects whose deployed runtime *is* a multi-agent system can canvas the running agents directly via their existing chat / API surface. The agents bring divergent priors (different model families, different memory state, different prompts) which makes them a high-quality pressure test. This is an *enhancement* available to such projects; the canvas pattern itself works without it.

### Anti-patterns

- **Consulting personas one at a time and stopping at the first ratification.** That's confirmation bias dressed as consensus. Run the canvas in parallel.
- **Counting votes.** Convergence is not voting. A 4-of-5 vote for the wrong answer is still wrong.
- **Discarding personas whose feedback you don't like.** If a persona keeps offering objections you reject, re-prompt to understand the objection, don't filter.
- **Letting the canvas run forever.** A canvas where consensus does not form within 2 rounds means the proposal needs rewriting, not more rounds. Reframe and re-canvas.

---

## Options

## Depth Control

| Flag | Effect |
| --- | --- |
| `--quick` | Brief feedback (1-2 sentences, 1-2 questions) |
| `--thorough` | Detailed analysis (full persona voice, comprehensive questions) |
| (default) | Standard depth (2-4 sentences, 2-4 questions) |

## Filtering

| Flag | Effect |
| --- | --- |
| `--relevant` | Only consult personas relevant to artefact type |
| `--persona [name]` | Consult specific persona only |
| `--exclude [name]` | Exclude specific persona |

## Team Override

| Flag | Effect |
| --- | --- |
| `--product [name]` | Use specific Product amigo representative |
| `--engineering [name]` | Use specific Engineering amigo representative |
| `--qa [name]` | Use specific QA amigo representative |

## Output

| Flag | Effect |
| --- | --- |
| `--output [file]` | Write to file instead of stdout |
| `--format [md\|json]` | Output format (default: md) |
| `--append` | Append to artefact as review section |

---

## Relevance Scoring {#relevance}

When using `--relevant`, personas are scored:

| Factor | Weight | Example |
| --- | --- | --- |
| Role match | 40% | Product Owner reviewing PRD = high |
| Expertise overlap | 30% | Security lead reviewing auth feature = high |
| Artefact mentions persona | 20% | PRD mentions "power users" = Emma relevant |
| Historical feedback acted upon | 10% | Previously useful feedback = higher weight |

Threshold: Personas scoring < 30% are skipped.

---

## Artefact-Specific Guidance {#artefact-guidance}

## PRD Review

**High-value personas:**

- Product (all) - Requirements completeness
- End Users - Does this solve their problem?
- Business - ROI and strategic alignment
- Security - Data handling concerns

**Focus areas:**

- Problem statement clarity
- Success metrics defined
- Scope boundaries
- User impact

## Epic Review

**High-value personas:**

- Product - Scope and prioritisation
- Engineering - Technical feasibility
- QA - Testability
- Affected user types

**Focus areas:**

- Size and complexity
- Dependencies
- Acceptance criteria quality

## Story Review

**High-value personas:**

- The specific persona in "As a..."
- QA Lead - Testable acceptance criteria
- Engineering - Implementation clarity

**Focus areas:**

- Acceptance criteria completeness
- Edge cases identified
- Persona needs addressed

## Technical Spec Review

**High-value personas:**

- Engineering (all) - Architecture quality
- Security - Vulnerabilities
- DevOps - Operational concerns

**Focus areas:**

- Technical approach
- Error handling
- Performance considerations

---

## Integration Points {#integration}

## Automatic Consultation (Workflow Integration)

Consult is triggered automatically in workflows (Three Amigos is the default for most artefacts):

| Workflow | Trigger | Default Personas |
| --- | --- | --- |
| PRD create | After draft complete | Three Amigos + relevant stakeholders |
| Epic create | After generation | Three Amigos + affected stakeholders |
| Story create | After cohesion review | Three Amigos (PO: completeness, Eng: TRD, QA: testability) |
| Story plan | After plan creation | Three Amigos (PO: scope, Eng: approach, QA: test strategy) |
| Bug fix | After root cause analysis | Three Amigos (PO: impact, Eng: root cause, QA: regression) |
| Bug verify | After fix complete | QA Lead |
| Spec review | Before implementation | Engineering team |

Disable with `--skip-personas` on parent command.

## Manual Integration

Add consultation to any workflow:

```bash
# After creating PRD
/sdlc-studio prd create
/sdlc-studio consult team sdlc-studio/prd.md

# Before implementing story
/sdlc-studio consult priya-sharma sdlc-studio/stories/US0001.md
```

---

## Consultation Prompt Template {#prompt-template}

```text
You are the {{seat_name}} review seat ({{role}}).

## Your Charter

**Mandate:** {{mandate}}

**Lens (your standing questions):**
{{lens}}

**Non-negotiables:** {{non_negotiables}}

**You push back when:** {{pushes_back_when}}

**Your shadow (how you fail when trying hardest to be good - guard against it):** {{shadow}}

**Authority:** approves {{approves}}; blocks {{blocks}}; defers {{defers}}

## Your Task

Review this {{artefact_type}} against your charter:

---
{{artefact_content}}
---

Respond AS the {{seat_name}} seat, in first person. Hold your stance under pressure - do not
default to agreement to keep the peace (watch your shadow).

Provide:

1. **Verdict:** Choose one:
   - ✅ Approve - Ready to proceed
   - ⚠️ Concerns - Can proceed with conditions
   - ❌ Reject - Cannot proceed until addressed

2. **Feedback:** 2-4 sentences in your voice explaining your verdict

3. **Questions:** 2-4 questions your lens raises

4. **Conditions:** (If Concerns or Reject) What must be addressed before you approve
```

---

## See Also

- `reference-persona.md` - Persona management
- `reference-chat.md` - Interactive persona sessions (Phase 5)
- `scripts/persona_resolve.py` - the declared-`role:` resolver consult and delegation share
- `templates/personas/amigo-template.md` - the enriched seat schema (the fallback charter)
- `help/consult.md` - Quick command reference
- `templates/reviews/consultation-*.md` - Output templates

---

## Navigation {#navigation}

**Prerequisites:**

- Personas must exist in `sdlc-studio/personas/`

**Related workflows:**

- `reference-prd.md` - PRD creation (consult after)
- `reference-story.md` - Story creation (consult persona)
- `reference-review.md` - Document review workflows

**Templates:**

- `templates/reviews/consultation-single.md`
- `templates/reviews/consultation-team.md`
- `templates/reviews/consultation-stakeholders.md`
