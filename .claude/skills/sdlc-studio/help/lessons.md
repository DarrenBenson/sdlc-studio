<!-- Load when: user runs /sdlc-studio lessons or asks about per-project failure memory -->
<!-- Dependencies: reference-agentic-lessons.md -->

# /sdlc-studio lessons - Help

> **Source of truth:** `reference-agentic-lessons.md#lessons-accumulation` - File format and hook points

Per-project failure memory. Each project accumulates its own lessons
in `sdlc-studio/.local/lessons.md`; agentic waves load this file at
wave start and inject the entries into every Agent Prompt Template
as a `## Known Pitfalls on This Project` section.

The file is never committed (`.local/` is gitignored). That is the
**per-project tier** – transient failure memory for agentic waves, and the
**default**: a lesson learned on this project is not automatically true on any
other, so `lessons add` (no flag) is where a lesson goes first.

There is also a **cross-project tier**: the skill's own `lessons/` folder,
carrying *generalisable* engineering/process lessons that improve decisions on
ANY project (it ships with the skill). **Recall** relevant ones before
substantive decisions; **promote** a project lesson there with `--global` only
once it clearly generalises - the deliberate act, not the reflex. Promotion
needs a version-controlled destination (`skill_source_repo`, below); without
one it is refused rather than written into a copy the next update deletes. A
project-specific *fact* (a config path, an incident, a box name) is **memory**,
not a lesson – keep those in the project's memory store.

All actions are backed by `python3 "$CLAUDE_SKILL_DIR/scripts/lessons.py"`
(`list` / `add` / `prune` / `recall` / `revalidate` / `summary`).

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "What have we learnt the hard way on this project?" | `/sdlc-studio lessons list` |
| "Note that down so we don't trip over it again" | `/sdlc-studio lessons add` |
| "Anything we should know before deciding this?" | `/sdlc-studio lessons recall` |
| "That mistake could bite any project - save it for all of them" | `/sdlc-studio lessons add --global` |
| "Clear out the old lessons from the early epics" | `/sdlc-studio lessons prune --older EP0003` |
| "Which lessons still hold?" | `/sdlc-studio lessons revalidate` |
| "Refresh the summary before we close the sprint" | `/sdlc-studio lessons summary` |

## Quick Reference

```bash
/sdlc-studio lessons list                      # Print accumulated lessons
/sdlc-studio lessons add                       # Interactive add (project tier - the default)
/sdlc-studio lessons add --epic EP0004 --wave 2  # Add with explicit context
/sdlc-studio lessons prune --older EP0003      # Drop entries tied to old epics

# The sprint close loop (gated - see below)
/sdlc-studio lessons revalidate                # List open lessons with their validity horizon
/sdlc-studio lessons revalidate --close L-0003 --reason "fixed upstream"   # unknown id: refused, not a no-op
/sdlc-studio lessons revalidate --extend L-0004  # Still true: push the horizon out
/sdlc-studio lessons revalidate --stamp        # Give horizon-less lessons a horizon (backfill)
/sdlc-studio lessons summary                   # Regenerate retros/LESSONS-SUMMARY.md

# Cross-project tier (skill lessons/ folder)
/sdlc-studio lessons recall                    # Surface relevant cross-project lessons before a decision
/sdlc-studio lessons recall --tags reconcile   # Filter by tag
/sdlc-studio lessons add --global              # Promote a generalisable lesson (needs skill_source_repo)
```

## The close loop is enforced, not advised

Lessons are summarised at the end of every sprint and read at the start of the next
one. Neither half depends on anyone remembering:

- **The close gate fails loud on a stale summary.** `gate --require-retro RETROxxxx`
  (or `--require-lessons`) recomputes the digest from the lessons log and compares it
  with the committed `sdlc-studio/retros/LESSONS-SUMMARY.md`. A lesson **closed** since
  the last regeneration fails it exactly as an added one does. The file is derived
  output - there is no freshness stamp to forge, and reformatting it cannot false-fire
  the check. Fix: `lessons summary`.
- **The close gate fails loud on an unre-validated lesson.** Every lesson carries a
  validity horizon (`Review-by:`, stamped at `add`; default 90 days, set
  `lessons.validity_days` in `sdlc-studio/.config.yaml`). Past it, the lesson is
  **closed** (`revalidate --close`, no longer true) or **extended** (`revalidate
  --extend`, still true). A lesson carrying no horizon at all is a finding too -
  `revalidate --stamp` backfills one.
- **The next sprint reads them without being asked.** `sprint plan` prints the
  still-valid lessons in the plan itself, so they arrive in the output the agent
  already reads - not as a pointer to a file it may not open.

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

### revalidate

List the open lessons with their validity horizon, or act on one. Unlike `prune`
(which deletes by epic age), `revalidate` records the judgement in the log: a closed
lesson stays readable, with its reason, and drops out of the summary digest.

**Usage:**

```text
/sdlc-studio lessons revalidate                          # List open lessons + horizons
/sdlc-studio lessons revalidate --close L-0003 --reason "schema now enforced in CI"
/sdlc-studio lessons revalidate --extend L-0004          # Still true: horizon moves out
/sdlc-studio lessons revalidate --extend L-0004 --days 30
/sdlc-studio lessons revalidate --stamp                  # Backfill missing horizons
```

### summary

Regenerate the committed `sdlc-studio/retros/LESSONS-SUMMARY.md` from the still-valid
lessons. Deterministic for a given log (no date in the output), so it is reproducible -
which is what lets the close gate recompute it and compare rather than trust it.

**Usage:**

```text
/sdlc-studio lessons summary                 # Rewrite retros/LESSONS-SUMMARY.md
/sdlc-studio lessons summary --dry-run       # Report without writing
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

**It writes only where git actually holds the file.** An installed or vendored
skill copy is a deployment artefact - the next update replaces the whole folder -
so a lesson authored inside it is deleted, silently. Three things are checked
before anything is written, and any of them failing is a refusal (non-zero exit,
with the remedy) rather than a write that will not survive:

1. the destination is inside a git work tree;
2. git is not **ignoring** it - a vendored `.claude/skills/` copy inside your own
   repo is usually gitignored, which passes (1) while git never sees the file;
3. the lessons registry itself (`_index.md`) is version-controlled, which is what
   makes `git status` show the new lesson.

The running skill's own folder is additionally required to *be* the skill source
checkout: committing a lesson into a vendored copy ships it with no release.
Give promotion a real destination, in the project's `sdlc-studio/.config.yaml`:

```yaml
skill_source_repo: ~/code/sdlc-studio   # your sdlc-studio source checkout
```

The lesson then lands in that checkout's `.claude/skills/sdlc-studio/lessons/`,
`git status` there shows it, and committing it ships the lesson with the next
skill release. That commit **is** the blessing path; there is no other. Without
the key, keep the lesson in the project tier (`lessons add`, no flag) until it
is worth promoting.

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
