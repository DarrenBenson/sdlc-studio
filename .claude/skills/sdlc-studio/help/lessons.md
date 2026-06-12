<!-- Load when: user runs /sdlc-studio lessons or asks about per-project failure memory -->
<!-- Dependencies: reference-agentic-lessons.md -->

# /sdlc-studio lessons - Help

> **Source of truth:** `reference-agentic-lessons.md#lessons-accumulation` - File format and hook points

Per-project failure memory. Each project accumulates its own lessons
in `sdlc-studio/.local/lessons.md`; agentic waves load this file at
wave start and inject the entries into every Agent Prompt Template
as a `## Known Pitfalls on This Project` section.

The file is never committed (`.local/` is gitignored). That is the
**per-project tier** – transient failure memory for agentic waves.

There is also a **cross-project tier**: the skill's own `lessons/` folder
(`~/.claude/skills/sdlc-studio/lessons/`), carrying *generalisable*
engineering/process lessons that improve decisions on ANY project (it ships
with the skill). **Recall** relevant ones before substantive decisions;
**promote** a project lesson there only once it clearly generalises. A
project-specific *fact* (a config path, an incident, a box name) is **memory**,
not a lesson – keep those in the project's memory store.

All actions are backed by `python3 "$CLAUDE_SKILL_DIR/scripts/lessons.py"`
(`list` / `add` / `prune` / `recall`).

## Quick Reference

```bash
/sdlc-studio lessons list                      # Print accumulated lessons
/sdlc-studio lessons add                       # Interactive add
/sdlc-studio lessons add --epic EP0004 --wave 2  # Add with explicit context
/sdlc-studio lessons prune --older EP0003      # Drop entries tied to old epics

# Cross-project tier (skill lessons/ folder)
/sdlc-studio lessons recall                    # Surface relevant cross-project lessons before a decision
/sdlc-studio lessons recall --tags reconcile   # Filter by tag
/sdlc-studio lessons add --global              # Promote a generalisable lesson into the skill's lessons/
```

## Actions

### list

Print the lessons file in reverse chronological order (newest first).

**What happens:**

1. Reads `sdlc-studio/.local/lessons.md`
2. If the file does not exist, prints a friendly message and exits 0
3. Otherwise prints each L-NNNN entry with its Epic, Wave, Symptom,
   Root cause, Fix, and Applies to fields

**Usage:**

```text
/sdlc-studio lessons list
```

### add

Append a new lesson to the file. Prompts interactively for the
fields if they are not passed on the command line.

**What happens:**

1. Creates `sdlc-studio/.local/lessons.md` with a header if absent
2. Assigns the next L-NNNN ID by scanning existing entries
3. Prompts for: epic, wave, symptom, root cause, fix, applies to
4. Inserts the new entry at the top of the file (below the header)
5. Updates `**Last Updated:**`

**Usage:**

```text
/sdlc-studio lessons add
/sdlc-studio lessons add --epic EP0004 --wave 2
```

**Interactive example:**

```text
> Epic: EP0004
> Wave: 2
> Symptom: Agent added `created_at` as camelCase; existing tests used snake_case
> Root cause: READ THESE FILES FIRST omitted src/db/schema.ts
> Fix: Added schema.ts to the repo_map hub-files list and every schema-touching prompt
> Applies to: Any story modifying the schema or adding fields
Wrote L-0003 to sdlc-studio/.local/lessons.md
```

### prune

Drop entries that refer to a specific epic (useful when epics are
superseded or when the project has diverged enough that old lessons
are noise).

**Usage:**

```text
/sdlc-studio lessons prune --older EP0003    # Drop lessons tied to EP0003 or older
/sdlc-studio lessons prune --epic EP0004     # Drop only EP0004 entries
```

## When to Add a Lesson

Four hook points, detailed in
`reference-agentic-lessons.md#lessons-accumulation`:

1. **Wave failure** - A wave went red (typecheck, tests, or merge).
   Record the cause and the fix that worked on the next attempt.
2. **Post-wave merge failure** - A hub file conflict or broken
   import sneaked past the Post-Wave Merge Protocol. Record which
   file and how to avoid next time.
3. **Epic retrospective** - After an epic ships, record any
   non-obvious pattern that surfaced during the run.
4. **Manual** - Any developer friction worth not repeating.

## Cross-project lessons (`recall` / `add --global`)

The skill's `lessons/` folder is a curated, durable knowledge base – see
`lessons/_index.md` and `lessons/_template.md`.

### recall
Read `lessons/_index.md`, surface the lessons whose tags/titles match the
decision at hand (optionally `--tags`), and apply them. Cheap, high-impact:
do this before any non-trivial design or process decision. The Operating
Doctrine (`reference-doctrine.md`) instructs this as a standing habit.

### add --global
Promote a generalisable lesson: next free `LL{NNNN}`, copy `lessons/_template.md`
(Lesson / Why-it-cost / How-to-apply / Generalises-to), add the index row.
Gate: it must apply *beyond* this project. Project facts go to memory instead.
Additions accumulate locally and are blessed into the next skill release.

## File Format

See `reference-agentic-lessons.md#lessons-accumulation` for the
canonical structure. Each entry is a markdown section with a fixed
set of fields:

```markdown
## L-0003: Short descriptive title

- **Epic:** EP0004
- **Wave:** 2
- **Symptom:** What went wrong (one sentence)
- **Root cause:** Why it happened (one or two sentences)
- **Fix:** The change that made it stop (one sentence)
- **Applies to:** Which future stories or patterns this affects
```

Keep entries under 10 lines. A lesson the next wave doesn't read is
a lesson wasted.

## Related Commands

- `/sdlc-studio epic implement --agentic` - Consumes
  `.local/lessons.md` at wave start
- `/sdlc-studio project implement --agentic` - Consumes lessons
  before each epic's Wave 1

## See Also

- `reference-agentic-lessons.md#lessons-accumulation` - Full rationale and format
- `reference-agent-prompt-template.md#agentic-execution` - Wave-start hook that reads the file
