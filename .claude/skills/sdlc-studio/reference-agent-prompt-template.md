# SDLC Studio Reference - Agent Prompt Template

<!-- Load when: building a worktree-agent prompt for epic/project agentic waves, or seeding READ THESE FILES FIRST for code plan -->

Canonical structure for the prompt each parallel implementation agent
receives during `epic implement --agentic` and `project implement
--agentic`. Consumed by `reference-epic.md` (wave execution),
`reference-project.md` (cross-epic orchestration), and
`reference-agentic-lessons.md` (pitfall injection).

## Contents

- [Prompt Structure](#agent-prompt-template) - the mandatory sections in order
- [Seat Framing](#seat-framing) - append the amigo stance after the contract
- [What Makes a Good Prompt](#good-prompt) - bad vs good examples
- [Building the Prompt](#agentic-execution) - orchestrator pre-work
- [Structured Clarifications](#structured-clarifications) - pause format
- [Inter-Epic Context](#inter-epic-context)

The quality of agentic implementation depends almost entirely on the prompt each worktree agent receives. A well-structured prompt replaces the plan file, test spec, and scope boundaries. A vague prompt produces inconsistent, low-quality code.

## Prompt Structure {#agent-prompt-template}

Every agentic implementation prompt MUST contain these sections in this order:

```markdown
## Task: Implement US{NNNN} - {Story Title}

{Framework} project. {One sentence of context about what this story does.}

### What to Build
{2-3 sentences describing the deliverable. Not the full AC - a human summary.}

### READ THESE FILES FIRST
{Numbered list of existing files the agent must read before writing anything.
Include what to look for in each file. This is the most important section -
it establishes the patterns the agent must follow.
**Populate this list from the repo map, not from memory.** Run
`python3 "$CLAUDE_SKILL_DIR/scripts/repo_map.py" query --story <story-path> --top 10` first and
use the output as the starting file set. Prune obvious false positives
and add any files the indexer missed (hub files, shared types, schema
definitions). If the repo map is absent or older than an hour, rebuild
first with `repo_map.py build`. See `reference-repo-map.md` for details.}

1. `src/lib/bridge/client.ts` - BridgeClient class, Zod schema pattern, error handling
2. `src/db/bridges.ts` - CRUD helper pattern (insertBridge, getBridge, etc.)
3. `src/app/bridges/page.tsx` - Server Component page pattern
4. `src/components/ui/badge.tsx` - shadcn Badge component
5. `vitest.config.ts` - Test configuration

### Acceptance Criteria
{Verbatim Given/When/Then from story file. Do not paraphrase.}

### Files to Create
{Explicit paths for new files this agent should create.}
- `src/lib/backup/engine.ts`
- `src/lib/backup/engine.test.ts`

### Files to Modify
{Explicit paths for existing files this agent should change.}
- `src/lib/bridge/client.ts` - Add getMetrics() method
- `src/db/schema.ts` - Add snapshots table

### DO NOT Modify
{Hub files or files being modified by other agents in this wave.}
- `src/app/page.tsx` (being modified by another agent)
- `src/app/layout.tsx` (hub file - integrate manually after)

### Codebase Patterns to Follow
{Key conventions extracted from READ THESE FILES FIRST.
Be specific - naming, imports, error handling, styling.}

- Server Components: `export const dynamic = 'force-dynamic'`, data via direct DB call
- Client Components: `'use client'`, useState for state, useRouter().refresh() after mutations
- Styling: Tailwind with `cn()` utility, `bg-card rounded-lg border border-border p-6`
- Errors: Custom error classes with `code` property, never throw raw strings
- IDs: `crypto.randomUUID()`, timestamps as ISO 8601 strings
- Imports: `@/` alias for `src/`

### Implementation Steps
{Ordered steps. Include code snippets for Zod schemas, interfaces, or
complex logic where the shape matters. Skip snippets for straightforward
CRUD or UI rendering.}

1. Add Zod schema to client.ts: `export const SnapshotSchema = z.object({ ... })`
2. Create engine.ts with backup flow: quiesce -> tar -> store -> resume
3. Write tests covering: success, storage failure, agent resume on failure

### Testing

{What to test. Minimum counts. Framework specifics.}

Write tests in `src/lib/backup/engine.test.ts`:

- Successful backup creates snapshot and stores archive
- Failed storage marks snapshot as failed
- Agent always resumed even on failure
- Audit entry logged

Use `vi.stubGlobal('fetch', fetchMock)` for HTTP mocks.
Use in-memory SQLite for DB tests.

### Quality Gates

{Non-negotiable requirements.}

1. `pnpm typecheck` - zero errors
2. `pnpm test` - all tests pass (existing + new)
3. No `any` types - use `unknown` with type guards
4. British English in comments and user-facing strings

```text

## Seat Framing {#seat-framing}

Each delegated worker is framed as an **amigo seat**, not a generic agent. After the
contract above is assembled, append the resolved amigo stance as the FINAL section of the prompt:

```bash
# build worker (the implementer):
python3 "$CLAUDE_SKILL_DIR/scripts/persona_resolve.py" resolve --seat engineering --render build --root .
# test worker (the QA author):
python3 "$CLAUDE_SKILL_DIR/scripts/persona_resolve.py" resolve --seat qa --render build --root .
```

The resolver picks the most-specific identity, most-specific-first:

1. an explicit practitioner amigo at `sdlc-studio/personas/amigos/<seat>.md` (the legacy filename
   override);
2. a **role-matched review seat** in `sdlc-studio/personas/seats/*.md` - the project's authored
   "Three Amigos", consulted as isolated subagents. Seats are named after people, so the resolver
   matches on a **declared role field**, the machine-readable `<!-- role: engineering -->` comment
   on the card, never the H1 prose or the filename. This is what stops a hand-authored seat from
   being shadowed by the generic default;
3. the skill default amigo (Dani / Sam / Lena);
4. nothing (the generic path).

The declared role field is deterministic at the boundary: two seat cards declaring one role resolve
lexically by filename and the resolver warns; zero declaring it falls through to the default and
never crashes. A resolved seat card requested for `--render review` that lacks its review-render
sections (Lens / Pushes Back When / Shadow) is a **hard error**, never a silent fallback to the
generic card - a half-authored seat is surfaced, not quietly dropped.

Four rules govern the framing, none negotiable:

1. **Stance after contract, never through it.** The amigo card is appended *after* Quality Gates as a
   disposition layer. It never rewrites or dilutes READ THESE FILES FIRST / Files to Create-Modify-DO
   NOT Modify / Acceptance Criteria / Quality Gates - those concrete sections are most of the build
   quality.
2. **Independence is the floor.** The build seat and the reviewing seat are always *separate
   instances*; the worker never reviews its own diff. The critic verdict records both ids and the
   conformance gate proves `reviewer != author`.
3. **`--skip-personas` is byte-equivalent.** With no personas the resolver emits nothing, so the
   prompt is the bare contract and must still build and pass the same gated executable ACs. If a
   build only works *with* the persona, the contract was underspecified - fix the contract.
4. **Green stays the oracle.** The QA seat authors and runs the tests, but pass/fail is `verify_ac`
   plus the conformance gate, never the seat's judgement.

## Plan-Review Charter {#plan-review-charter}

Before a story with spec-derived ACs is implemented, an independent reviewer challenges its
ACs against the source spec (the deterministic `plan_review` gate - see
`reference-config.md#plan-review`). This closes the N=5 "bad plan propagates" failure: a
planner mis-pinned a spec rule in the ACs and the delivery critic, whose oracle IS the ACs,
approved a faithful build of the wrong plan.

The reviewer is the **QA / tester seat's review render** (`persona_resolve.py resolve --seat
qa --render review`), always a *separate instance from the plan's author* - the same
independence floor as the delivery critic (`reviewer != author`, proven by the gate). The
charter, appended after the contract like any seat render:

1. **Re-read the cited source.** For each AC that references a spec/requirements document,
   open the cited section and read the actual rule - do not trust the AC's paraphrase.
2. **Challenge each spec-derived AC against its source.** Does the AC faithfully restate the
   rule, or does it **contradict or invert** it? An AC that inverts the source (the R5-inversion
   failure mode) is a **blocking finding**, not a style note.
3. **Default mode is challenge-the-written-ACs** (cheaper, ADR-006-friendly). For a unit whose
   routed difficulty band is **high or above**, escalate to **blind re-derivation**: derive the
   constraining requirements from the source *without reading the ACs first*, then diff - it
   catches an inversion that anchoring on the written AC would miss.
4. **Record with `plan_review record`** (not the bare `critic record` form): it pins the verdict
   to the exact ACs reviewed by fingerprint, so a later AC edit invalidates the approval. A
   REJECT blocks implementation until the ACs are corrected and re-reviewed.

## Delivery-Review Charter: untraced spec edits {#spec-edit-charter}

The delivery critic (the QA seat reviewing the finished diff) has one non-negotiable check
beyond judging the diff against AC intent: **an untraced spec edit is a blocking finding, not a
style note.** In the N=5 benchmark a worker edited the requirements spec to state the inverse of
the real rule so its wrong implementation would pass - falsifying the source of truth, which
poisons every later reader including auditors and future planners.

Run the deterministic pre-check first: `spec_guard.py check --changed <git diff --name-only>
--story <story file>`. Per edited file, it reports which changed files are requirements/spec
documents (config `review.spec_paths`) and which of them the story never references. Then judge:

- An **untraced spec edit** - an edited `review.spec_paths` file the story never references - is
  a **blocking finding**. Do not approve until the edit is reverted or justified by an explicit
  requirement in the ticket/story/CR.
- A **referenced spec edit** - the story names the edited file - is NOT automatically fine: a
  reference is not a change-request (a `Verify: grep` line or an `Affects:` header names a spec
  without asking to edit it). Confirm the story actually **asked for this change** before
  approving.

The pre-check guarantees each spec edit is surfaced and matches per-file (an untraced edit
cannot ride on a mention of a different spec); the traceability judgement is yours.

## Tier Routing {#tier-routing}

With `routing.enabled`, each unit in the sprint plan carries a `tier` and
`model` recommendation. The orchestrator passes the model id to its own worker-spawn
mechanism (the id is an opaque string - the skill never calls a model API). Three rules:

1. **The prompt contract is byte-identical across tiers.** The sections above never
   change based on which model runs them - the exact analogue of seat-framing rule 3.
   If a unit only succeeds on a bigger model because the contract was vague, the
   contract was underspecified: fix the contract, not the tier.
2. **Overrides go to the ledger.** The recommendation is advisory; an orchestrator that
   overrides it records the override + rationale in the tranche ledger, so
   `tier_recommended` vs `tier_delivered` (telemetry) stays honest.
3. **The critic's tier comes from `route.py pick --role critic`** - never smaller than
   the author's, medium-floored for code units. Independence (a separate instance,
   reviewer != author) is unchanged by routing.

See `reference-sprint.md#model-tier-routing` for the full policy and escalation rule.

## What Makes a Good Prompt {#good-prompt}

| Aspect | Bad | Good |
| --- | --- | --- |
| Scope | "Implement the backup feature" | "Create `src/lib/backup/engine.ts` with quiesce/tar/store/resume flow" |
| Patterns | "Follow existing patterns" | "Use `cn()` from `src/lib/utils.ts`, `bg-card` class for cards" |
| Files | "Create necessary files" | Explicit list of files to create AND modify |
| AC | Paraphrased | Verbatim Given/When/Then from story |
| Exclusions | None | "DO NOT modify src/app/page.tsx" |
| Tests | "Write tests" | "8 tests covering: success, failure, edge case X, edge case Y" |
| Context | None | "READ THESE FILES FIRST: 1. client.ts for Zod pattern..." |
| Temp files | A shared scratchpad path | "Write any temp file INSIDE your own worktree" - a shared path collides between parallel agents |

### Parallel delegation: name the workspace, not only the files {#parallel-workspace}

When several agents deliver one batch at once, tell each to keep its temporary files - a commit
message, a fields-file, a worklist - inside its OWN worktree. A shared temp directory is not
isolated by a worktree, and one agent's file is overwritten by another between write and use: a
commit has landed carrying a different agent's subject this way. Namespace the path per agent, or
keep it in the worktree.

Say the same about the build tooling: an agent changing the pre-commit hook, the gate, or a guard
the commit path runs is changing the machinery every other agent commits through, however disjoint
its declared files look.

## Building the Prompt {#agentic-execution}

Before writing the prompt, the orchestrator MUST:

1. **Explore the codebase** (or use an Explore agent) to understand:
   - File structure and naming conventions
   - Existing patterns for the type of code being written
   - Canonical type locations (where shared interfaces live)
   - Test patterns (mocking approach, assertion style)
   - Hub files that multiple stories touch

2. **Read key files** to extract concrete patterns (not guesses):
   - The main layout/entry point
   - An existing page similar to what the story creates
   - An existing test file for the testing pattern
   - The database schema
   - The relevant client/service module

3. **Map story AC to file changes** to determine:
   - Which files need creating (agent's exclusive scope)
   - Which files need modifying (check for hub file conflicts)
   - Which files should NOT be touched (other agents' scope)

This exploration typically happens ONCE per epic (before wave 1) and the findings are reused across all waves in that epic. The key files, patterns, and conventions don't change within an epic.

**Also load `.local/lessons.md` at wave start** (cheap, file-only). If the file exists, inject a condensed `## Known Pitfalls on This Project` section into every Agent Prompt Template. Each lesson records a past failure from this specific project and the fix that worked. Skipping this step means the wave starts as dumb as the first one. See `reference-agentic-lessons.md#lessons-accumulation` for the format and four hook points.

## Structured Clarifications {#structured-clarifications}

When an agent (or the orchestrator) must pause on ambiguity, it poses a
**structured question with suggested answers**, never an open prose
question. Pre-thinking the likely answers turns a paragraph-writing
interruption into a ten-second decision, and the recorded choice is
unambiguous when the workflow resumes.

Format (in the pause report or AskUserQuestion call):

```text
Question: How should the login flow handle API errors?
  A. Return 401 with the error message in the response body
  B. Return 401 with an error code; client maps it to a local message
  C. Throw and let middleware translate (matches src/api/middleware.ts)
Suggested: C - consistent with the existing error pipeline.
(Or reply with your own answer.)
```

Rules: 2-4 concrete options; state which option the codebase evidence
favours and why; record the answer in the workflow file's notes so a
resumed session does not re-ask. See
`reference-decisions.md#execution-contract` for *when* pausing is
justified at all - structure governs *how* to ask, not whether.

## Inter-Epic Context {#inter-epic-context}

When implementing later epics that depend on earlier ones (e.g. EP0004 depends on EP0001):

- Earlier epic code is already committed to git HEAD
- Agent prompts should reference files from earlier epics in "READ THESE FILES FIRST"
- Example: EP0004 agents should read `src/lib/bridge/client.ts` (from EP0001) to understand BridgeClient patterns
- The commit strategy (per-epic) ensures earlier code is available to later agents
