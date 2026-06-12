# SDLC Studio Reference - Agent Prompt Template

<!-- Load when: building a worktree-agent prompt for epic/project agentic waves, or seeding READ THESE FILES FIRST for code plan -->

Canonical structure for the prompt each parallel implementation agent
receives during `epic implement --agentic` and `project implement
--agentic`. Consumed by `reference-epic.md` (wave execution),
`reference-project.md` (cross-epic orchestration), and
`reference-agentic-lessons.md` (pitfall injection).

## Contents

- [Prompt Structure](#agent-prompt-template) - the mandatory sections in order
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
