<!--
Load when: /sdlc-studio persona or /sdlc-studio persona help
Dependencies: SKILL.md (always loaded first)
Related: reference-persona.md, reference-persona-generate.md, reference-persona-learning.md
-->

# /sdlc-studio persona - User Personas

> **Personas are working seats, not static artifacts.** They consult on designs,
> seat-score the backlog, review diffs, and hold the author != reviewer gate - Alan
> Cooper's goal-directed personas brought to life. Resolve a seat for any review with
> `persona_resolve.py resolve --seat <role> --render review`.

## persona generate --team / --stakeholders

Grow the working team and the stakeholder panel from the project itself - fresh named
individuals per project (the shipped Dani/Sam/Lena cards remain the zero-setup fallback).
Analyse -> present discoveries -> ask at most 4 multi-choice questions (1 with `--quick`)
-> generate into `personas/seats/` and `personas/stakeholders/` -> stamp, `validate seats --require-stamp <written cards>`,
batch-accept. Never clobbers an authored or operator-edited card (content-hash guard);
detects legacy `personas/amigos/` shadowing and routes through the upgrade migration.
Standalone-runnable from a bare repo (repo-map analysis only) - no PRD required, though the
PRD gives the richest input. Full flow: `reference-persona-generate.md#team-generation`.

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Who are the users of this product?" | `/sdlc-studio persona list` |
| "Build out the people we are designing for" | `/sdlc-studio persona create` |
| "Work out the user types from our requirements" | `/sdlc-studio persona generate --from-prd` |
| "Figure out the users from the existing code" | `/sdlc-studio persona generate --from-code` |
| "Take another look at our personas and tidy them up" | `/sdlc-studio persona review` |
| "Bring in this persona file we already have" | `/sdlc-studio persona import [file]` |

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
| **Team** | Internal team (Three Amigos) | Product Owner, Developer, QA Lead |
| **Stakeholder** | External users and business | End User, Executive, Security |

### Three Amigos (Team)

| Amigo | Focus | Seat |
| --- | --- | --- |
| Product | What & Why | Product amigo: `persona_resolve.py resolve --seat product` |
| Engineering | How | Engineering amigo: `persona_resolve.py resolve --seat engineering` |
| QA | What If | QA amigo: `persona_resolve.py resolve --seat qa` |

A project seat card overrides the shipped one. The team archetype seeds in
`reference-persona.md#archetypes` are sample personas to start `persona create` from, not amigos.

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
| ------ | -------- | ---------- |
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

<!-- sample-personas -->
**Output** (sample personas from the archetype seeds; a team persona listed here is not an amigo):

```
TEAM PERSONAS

Product:
  Sarah Chen (PO) - Strategic decisions, scope control

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

<!-- /sample-personas -->

### export

Export a persona for use in other projects.

```
/sdlc-studio persona export sarah-chen
```

Copies the persona file to a specified location or clipboard.

### review

Review and refine existing personas.

**What happens:**

1. Loads all persona files and runs `persona_review.py check` on them
2. For each card, briefs a seat other than the card's own to review it against the standard
3. Records each verdict in `sdlc-studio/reviews/persona-reviews.md`
4. Asks if new personas are needed, then updates files and index

```bash
# Brief the product seat to review the qa seat's card (never the qa seat itself)
python3 scripts/persona_review.py brief --card sdlc-studio/personas/seats/qa.md --seat product

# Record its verdict against the card's body hash; a FAIL names each rule it failed
python3 scripts/persona_review.py record --card sdlc-studio/personas/seats/qa.md \
  --outcome fail --reviewer "Lena Marsh (product)" --run-by "Dana Fox" --rule persona-evidence
```

`--run-by` names the person who ran the review and defaults to `git config user.name`.
A PASS is refused while a rule that blocks still fails on the card, and a PASS on a
generated card clears its provisional stamp, as `persona_gen.py accept` does.

A project seat card that breaks a blocking rule, or whose latest review is a FAIL, frames
nothing until it is fixed or a later PASS is recorded: `persona_resolve.py resolve` and
`resolve-consult` exit 1, and `critic.py brief`, `refine.py apply` and `triage.py apply` exit
2, each naming the card, the rule and the command to run next. No other card stands in:

```text
sdlc-studio/personas/seats/qa.md breaks the persona standard (best-practices/persona.md), ...
  seat-demographic-fluff (Identity): demographic token '42 years old' - ...
Run next: python3 scripts/persona_review.py brief --card sdlc-studio/personas/seats/qa.md --seat engineering
```

When every other seat's own card is held too, that last line says no seat is clear and how
to lift one, in place of a command; `persona_review.py brief` refuses a held reviewing seat
with exit 2 and that seat card's own refusal. A card with no review, or changed since its
PASS, still frames, and one stderr line names it as owed its persona review.

`personas.standard` in `.config.yaml` sets that refusal. `block`, the default, refuses as
above; `report` frames the card and prints one `persona card blocked (report mode):` line on
stderr naming it, each rule it breaks and the command to run next. `migrate --apply` sets
`report` for a project holding its own cards with no value set; set `block` to switch the
standard on. See [the key](../reference-config.md#personas-staleness-days) and
[the persona standard](../reference-persona.md#persona-rules).

`persona_review.py owed` lists every card owed a review, and exits 0 whatever it finds:

```text
persona review owed: sdlc-studio/personas/seats/qa.md - changed since its review of 2026-11-02. Run next: python3 scripts/persona_review.py brief --card sdlc-studio/personas/seats/qa.md --seat engineering
persona review owed: sdlc-studio/personas/jonah-reyes.md - never reviewed. Run next: python3 scripts/persona_review.py brief --card sdlc-studio/personas/jonah-reyes.md --seat engineering
persona reviews owed: 2 (reported, never refused; each line ends in the command that briefs its review)
```

A card last passed before the newest release tag's commit is owed too, compared by day.
`sprint.py plan` prints the count as `persona reviews owed: <count>` and one `persona card
blocked:` line for each card the standard holds, with its remedy; `release_cut.py
changelog-cut` prints each owed card. Neither refuses for an owed review. A card whose bytes
are not UTF-8 is held as `card-not-utf8`, naming the line of its first such byte, and its
remedy is to save it as UTF-8; every other card is still judged.

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

## Archetype Seeds

Generate any of these on demand with `persona create --from-archetype <slug>` - the
skill ships the seeds (role + disposition) + `persona-template.md`, not baked character
files:

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
- `reference-persona-learning.md` - A persona's memory: `persona_memory.py add`, `list` and `recall`, how its learnings reach a brief, and how a seat writes one from a retro (`learn-brief`, `propose`) and another seat approves it (`approve-brief`, `approve`)
- `reference-philosophy.md#generate-mode` - Generate mode philosophy

**Related commands:**

- `/sdlc-studio prd help` - Product requirements (upstream)
- `/sdlc-studio story help` - User Stories (downstream)
- `/sdlc-studio consult help` - Persona consultation (Phase 3)
