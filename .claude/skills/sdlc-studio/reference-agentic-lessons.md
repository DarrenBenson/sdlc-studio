# Agentic Implementation Lessons

Hard-won lessons from production runs of `epic implement --agentic` and `project implement --agentic`. Read this before any agentic execution.

<!-- Load when: running epic implement --agentic, project implement --agentic, or project implement -->

These are not procedures - they are patterns observed across real project implementations that consistently affect quality and speed. Treat them as constraints on your approach.

> **Scope note.** This file is narrowly about agentic wave execution. For cross-cutting operator patterns (memory-entry drift, silent-CLI-failure localisation, post-release briefing, adversarial-review-as-gate) see **`reference-operator-heuristics.md`**. For project-specific pitfalls see `sdlc-studio/.local/lessons.md` (see `help/lessons.md`).

---

## Exploration

### Load project lessons before exploration

At the start of every wave, load `sdlc-studio/.local/lessons.md` if
it exists. This file accumulates failure patterns specific to the
current project (not generic advice). Inject the entries into the
Agent Prompt Template as a `## Known Pitfalls on This Project`
section so agents avoid repeating them. Greenfield projects without
the file skip this step entirely. See the "Lessons Accumulation"
section below for the format and hook points.

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

### Commit every wave to main before launching the next wave's worktree agents

The per-epic commit rule is not enough. `Agent({ isolation: 'worktree' })` branches from a HEAD cached at an earlier agent-tool invocation, not the current main HEAD, so a Wave 2 agent can branch from a pre-Wave-1 baseline and never see the types or files Wave 1 added. The fix is to **commit each wave to main before launching the next wave's worktree agents** - the HEAD a worktree branches from must already include every prior wave.

When stale-HEAD still happens, recover by extracting the agent's work as a diff against its stale base and replaying it on main (`git diff HEAD -- <files> > /tmp/patch` then `git apply /tmp/patch`), rather than re-running the agent.

### Single-agent-on-main is the default; parallel worktrees are the exception

Most waves should run as a single agent committing straight to main. Opt into parallel worktrees only when all three hold:

- both stories have **hermetic file scopes** (zero shared hub files);
- the combined story points exceed ~10 SP, so parallelism saves material wall-clock; and
- the **merge plan is written before launch** (which files are copied, which are merged by hand).

Below that bar the merge overhead exceeds the throughput gain. A 19 SP epic shipped in six sequential waves often matches the wall-clock of a botched three-parallel-wave run.

### Cherry-pick worktree branches by scope narrowness, not story points or id

When merging parallel worktrees, land the **narrowest-scope** change first; surgical changes merge cleanly on top of larger additions, whereas the reverse creates three-way conflicts. Order by blast radius, not by SP or story number.

### Wave 1 forward-declares every shared type, interface, and hub-file addition

The foundation wave must enumerate and create the shared surface later waves consume - types, interfaces, and the test-fixture surface - as a forward scaffold. Waves 2+ then implement against that scaffold and never touch the shared file, so the parallel adapters carry zero conflict. Derive the shared-file set from `scripts/repo_map.py`, not from memory.

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

**Derive the list from the repo map, not from memory.** Run
`scripts/repo_map.py query --story <story-path> --top 10` first and
use the output as the starting file set. Human memory is unreliable on
codebases above 10 kloc; the indexer is not. See
`reference-repo-map.md` for details. Then prune and augment by
judgment to prioritise:

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

---

## Lessons Accumulation {#lessons-accumulation}

This document is generic: battle-tested patterns that apply to any
project. It does not know your specific codebase's quirks. The
per-project lessons file closes that gap.

### Where lessons are stored

`sdlc-studio/.local/lessons.md`. The file is never committed
(`.local/` is already gitignored) and is created lazily on first
append.

### When lessons are recorded

Four hook points:

1. **Wave failure** - When an agentic wave fails (typecheck red,
   tests red, or the Post-Wave Merge Protocol fails), append a
   lesson naming the root cause and the fix that made the next
   attempt work.
2. **Post-wave merge failure** - When the merge step produces
   conflicts or broken imports, append a lesson describing which
   hub file was involved and how the sidecar pattern could have
   avoided it.
3. **Epic completion retrospective** - After each epic, optionally
   add a lesson capturing any non-obvious pattern that emerged
   (naming conventions, testing gotchas, schema surprises).
4. **Manual entry via `/sdlc-studio lessons add`** - Any time a
   developer notices a recurring friction and wants to record it.

The mechanical work - ID allocation, top-of-file insertion, header
upkeep, pruning - is scripted. Claude gathers the lesson content
(the judgement), then runs `scripts/lessons.py`:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/lessons.py" list
python3 "$CLAUDE_SKILL_DIR/scripts/lessons.py" add \
  --title "Zod schema mismatch in wave 2" \
  --body "..." --epic EP0004 --wave 2
python3 "$CLAUDE_SKILL_DIR/scripts/lessons.py" prune --older EP0003
```

The script creates the file (with header) on first append, assigns
the next L-NNNN, inserts the entry at the top, and refreshes
`**Last Updated:**`.

### The project tier is the default; `--global` is the promotion

A lesson learned on one project is not automatically true on the next. Record
it where it was learned - `lessons add`, no flag - and promote it only once it
clearly generalises beyond this repo. Cheap and reversible; the reverse (a local
quirk asserted as a cross-project rule) is neither.

Promotion is `add --global`: next LL id from `lessons/_template.md`, index row
appended. It writes **only where git actually holds the file** - the lessons
registry it appends to must be version-controlled, not merely sitting inside a
work tree. Membership alone is not survival: a vendored skill copy under the
consuming project's `.claude/skills/` is inside that work tree and is normally
gitignored, so git never sees the lesson and the next install deletes it. An
installed or vendored copy is a deployment artefact - the update replaces the
folder - so `add --global` refuses that write (non-zero exit, naming the reason
and the remedy) rather than reporting a success it did not achieve.

Give promotion a tracked destination in the project's `sdlc-studio/.config.yaml`:

```yaml
skill_source_repo: ~/code/sdlc-studio   # the sdlc-studio source checkout
```

The lesson lands in that checkout's `.claude/skills/sdlc-studio/lessons/`,
`git status` shows it, and the commit that lands it ships it with the next skill
release. That commit is the whole promotion mechanism - nothing else "blesses" a
lesson into a release. Whether a lesson generalises enough to promote stays a
judgement call: see `help/lessons.md` and `reference-config.md#skill-source-repo`.

### File format

```markdown
# Project Lessons

**Last Updated:** 2026-04-15

<!-- Append new entries at the top. Keep each entry under 10 lines. -->

## L-0003: Zod schema mismatch in wave 2

- **Epic:** EP0004
- **Wave:** 2
- **Symptom:** Agent added `created_at` to the service schema as
  camelCase but existing tests expected snake_case
- **Root cause:** `READ THESE FILES FIRST` omitted `src/db/schema.ts`
  so the agent guessed the naming convention
- **Fix:** Added `src/db/schema.ts` to the repo_map hub-files list
  and to every prompt that touches schemas
- **Applies to:** Any story modifying the schema or adding fields

## L-0002: ...
```

Each entry has a monotonic L-NNNN ID, an epic/wave context, a
symptom, root cause, fix, and an "applies to" clause that helps
agents decide whether the lesson is relevant to the current story.

### How lessons are consumed

At wave start, the workflow described in
`reference-agent-prompt-template.md#agentic-execution` reads `.local/lessons.md` and
injects a condensed `## Known Pitfalls on This Project` section into
every Agent Prompt Template. Agents read this alongside
`reference-agentic-lessons.md` and the story-specific prompt. The
goal is for each wave to start smarter than the last.
