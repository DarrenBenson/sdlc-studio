# Agentic Implementation Lessons

Hard-won lessons from production runs of `epic implement --agentic` and `project implement --agentic`. Read this before any agentic execution.

<!-- Load when: running epic implement --agentic, project implement --agentic, or project implement -->

These are not procedures - they are patterns observed across real project implementations that consistently affect quality and speed. Treat them as constraints on your approach.

---

## Exploration

### Explore once per epic, not per wave

Before launching Wave 1 of an epic, run a single thorough codebase exploration covering:

- File structure and naming conventions
- Existing patterns for the type of code being written (pages, services, tests)
- Hub files that multiple stories will touch
- Canonical type/interface locations
- Test patterns (mocking approach, fixture style, assertion conventions)

Reuse these findings for every wave in that epic. The codebase patterns don't change within an epic. Repeating exploration per wave wastes time and context.

### Read, don't guess

Before writing any agent prompt, READ the actual source files you're referencing. Don't rely on memory of what a file contains - patterns drift across waves as agents modify files. Always verify the current state of:

- The module the agent will extend (it may have new methods from a prior wave)
- The test file for that module (the agent should match existing test style)
- The page or component being modified (it may have new sections)

---

## Wave Structure

### Wave 1 is always sequential

The first wave of every epic implements the foundation story - the one everything else depends on. Never try to parallelise it. This story establishes:

- New module directories
- Core interfaces and types
- Base patterns that all subsequent stories follow

Run it as a single foreground agent. Verify, commit, then plan parallel waves from Wave 2 onwards.

### Two parallel stories per wave is the sweet spot

Three or more parallel agents create merge complexity that outweighs the time saved. Two agents with clearly separated file scopes merge cleanly almost every time. Three agents touching the same layer almost always produce conflicts.

### Put the complex story in its own wave

If one story is 8 points and another is 3, don't parallelise them. The 3-point story finishes while the 8-point story is still running, wasting the parallelism. Pair stories of similar complexity.

---

## Agent Prompts

### "DO NOT" sections prevent scope creep

Without explicit exclusions, agents drift into neighbouring stories' scope. They add nav links that another story handles, modify layout files that are hub files, or implement features from the next wave's stories. Always include:

```text
### DO NOT
- Modify src/app/layout.tsx (hub file)
- Add agent detail pages (that's US0010)
- Implement polling (that's US0013)
```

### "READ THESE FILES FIRST" is the most important section

Agents that read existing code before writing new code produce dramatically better results. Agents that don't read first invent their own patterns, leading to inconsistent code that fails typecheck or doesn't match the project's conventions.

List 5-10 files with what to look for in each. Prioritise:

1. The module being extended (for API patterns)
2. A similar page/component (for UI patterns)
3. An existing test file (for test conventions)
4. The database schema (for data model)
5. The global stylesheet or theme (for styling)

### Concrete beats abstract

| Instruction | Result |
| --- | --- |
| "Follow existing patterns" | Agent invents patterns that look plausible but don't match |
| "Use `cn()` from `src/lib/utils.ts`, cards use `bg-card rounded-lg border border-border p-6`" | Agent produces consistent styling |
| "Write tests" | Agent writes 2-3 shallow tests |
| "Write 8 tests covering: success, storage failure, agent resume on failure, audit logged..." | Agent writes thorough, targeted tests |
| "Handle errors" | Agent adds generic try/catch |
| "Throw `BridgeClientError('BRIDGE_UNREACHABLE', message)` on network failure" | Agent uses the project's error pattern |

### Include code snippets for shapes, not logic

Agent prompts should include Zod schemas, interface definitions, and type shapes - anything where the exact structure matters. Don't include implementation logic - the agent can figure out how to implement a function, but it can't guess the right field names for an API contract.

---

## Hub Files and Merging

### Hub file conflicts are the #1 merge issue

Files that multiple stories modify (layout, router config, shared types, index files) cause the majority of merge problems. The sidecar pattern prevents 90% of them:

**Instead of:** Agent modifies `src/app/layout.tsx` to add a nav link
**Do:** Agent creates the page/component only. Orchestrator adds the nav link to layout after merge.

**Instead of:** Agent adds routes to `src/app/api/fleet/route.ts`
**Do:** Agent creates `src/app/api/fleet/agents/route.ts` (new file). No conflict possible.

### New files never conflict

Two agents creating different new files in the same directory is always safe. The wave analysis should maximise new-file stories in parallel and isolate modify-existing-file stories.

### Copy, don't merge

After a wave, copy files from worktrees rather than attempting git merge. Git merge between worktree branches and main creates unnecessary complexity. The pattern is:

1. `cp` new files from each worktree to main
2. `cp` modified files if only one agent touched them
3. Manual `Edit` for files both agents touched (rare if wave analysis is correct)

---

## Quality and Drift

### Per-wave reconcile is cheap but essential

Running `reconcile --scope stories` after each wave takes seconds but prevents the drift snowball. Without it, a 10-story epic accumulates 10 stories of stale index entries, unchecked dependency tables, and wrong status counts. The bulk reconcile at the end becomes a 60+ fix operation.

### Typecheck catches 80% of merge issues instantly

Run `pnpm typecheck` (or equivalent) immediately after copying files from worktrees. Most merge problems manifest as type errors: missing imports, incompatible interfaces, duplicate type definitions. Fix these before running the test suite.

### Test the merged code, not the worktree code

Worktree tests passing doesn't guarantee merged code works. Each worktree has its own isolated state. After merging both agents' changes, run the FULL test suite from the main directory. New failures indicate merge conflicts the agents couldn't predict.

---

## Commits and Pacing

### Per-epic commits are the sweet spot

Per-wave commits create noise (25+ commits for a 10-story epic with 4 waves). Per-project commits are risky (one bad merge corrupts everything). Per-epic commits give you:

- One logical unit per commit (the feature/epic)
- Easy revert if an epic's code is fundamentally wrong
- Clean `git log` for humans reviewing the work

### Commit sdlc-studio changes separately

Status updates, story promotions, and reconcile changes should be their own commit, not mixed with feature code. This keeps feature commits clean and makes it easy to revert sdlc-studio bookkeeping without touching code.

### Don't skip the post-epic commit

Even if the next epic depends on this one and you want to keep going, COMMIT before starting the next epic. Worktree agents branch from HEAD. If HEAD doesn't include the prior epic's code, the next epic's agents can't see it and will fail or reinvent types.

---

## Scale and Context

### Context window management matters at project scale

By epic 5 of 8, the conversation is long. Consider:

- Summarising completed epics ("EP0002 done: 8 stories, 241 tests, dashboard + agent detail pages")
- Not re-reading files that haven't changed since the last read
- Keeping wave analysis outputs brief (table, not prose)

### Story generation is its own phase

Don't generate stories and implement them in the same wave of thinking. Generate all stories for an epic (or all epics), review them, promote to Ready, THEN implement. Mixing generation and implementation leads to stories that are written to match code rather than code that implements stories.

---

## Common Failure Modes

| Failure | Cause | Prevention |
| --- | --- | --- |
| Agent creates wrong file structure | No "READ THESE FILES FIRST" section | Always include 5-10 reference files |
| Tests use different mock pattern | Agent didn't read existing test files | Include test file in READ FIRST list |
| Type errors after merge | Agent defined types locally instead of importing | Include "Canonical type locations" in prompt |
| Agent modifies hub file despite instructions | "DO NOT" section missing or too vague | Be explicit: list the exact file paths |
| Styling inconsistent | Agent guessed Tailwind classes | Include concrete class examples from codebase |
| Tests pass in worktree, fail after merge | Agents imported conflicting versions of a type | Run typecheck + tests on merged code, not worktree |
| Massive reconcile at the end | No per-wave reconcile | Add `reconcile --scope stories` after every wave |
| Agent implements too much | No scope exclusions | Always include "DO NOT" and "Out of Scope" sections |
