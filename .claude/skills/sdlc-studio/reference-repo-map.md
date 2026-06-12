# SDLC Studio Reference - Repo Map

Pure-Python repository indexer. Produces a ranked file list for the
`READ THESE FILES FIRST` section of the Agent Prompt Template and for
the initial file set during `code plan`. Replaces the hand-authored
"I think the agent needs these files" guess with a derivation from
the actual codebase.

<!-- Load when: building or querying the repo map, writing an Agent Prompt Template, or planning code for a story -->

## Reading Guide

| Section | When to Read |
| --- | --- |
| Why It Exists | When deciding whether to use the repo map for a workflow |
| When to Rebuild | When deciding if the index is fresh enough |
| Building | When running `/sdlc-studio repo map build` |
| Querying | When populating a `READ THESE FILES FIRST` section |
| Scoring | When interpreting query results or tuning relevance |
| Limits and Falsehoods | When an expected file is missing from results |
| Integration | When wiring repo map into new workflows |

## Why It Exists {#repo-map-why}

The Agent Prompt Template's `READ THESE FILES FIRST` section is the
single biggest determinant of agentic wave success. Production runs
show that when the list is correct, agents write correct code the
first time. When the list omits a canonical interface file or a shared
type definition, agents hallucinate APIs and the wave fails.

Through v1.5.0, the list was hand-authored per story from the human
author's memory of the codebase. On projects above 10,000 lines this
breaks down: nobody remembers every hub file, every schema, every
adapter. The repo map derives the list mechanically from the
codebase itself so the starting point is always correct.

The ranking is advisory, not prescriptive. Authors still prune and
augment the list, but they start from a real file set, not a guess.

## When to Rebuild {#repo-map-rebuild}

Build the index:

- **On init:** After `/sdlc-studio init` in a new project
- **Before an epic:** As part of `/sdlc-studio epic plan --epic EP0001`
  (agentic mode mandates this)
- **After a big refactor:** Whenever significant file moves or renames
  happen
- **When stale:** If `.local/repo-map.json` is older than an hour during
  active coding, or older than a day otherwise

The build is fast – a 50,000-line repo indexes in 5-15 seconds on
stock hardware. There is no significant cost to rebuilding more often
than strictly needed.

## Building {#repo-map-build}

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/repo_map.py" build \
  --root . \
  --out sdlc-studio/.local/repo-map.json
```

Options:

- `--root <path>`: Repository root to index. Default: current directory.
- `--out <path>`: Output JSON path. Default:
  `sdlc-studio/.local/repo-map.json`.
- `--ignore <dirname>`: Additional directory name to skip. Repeatable.
  Default ignores: `.git`, `node_modules`, `__pycache__`, `dist`,
  `build`, `target`, `.venv`, and 20+ other common noise directories.

The index is stdlib-only JSON with per-file symbols, imports, and an
in-degree score. Index structure is documented in
`scripts/repo_map.py`.

## Querying {#repo-map-query}

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/repo_map.py" query \
  --story sdlc-studio/stories/US0001-user-login.md \
  --top 10
```

`--story` accepts either a story file path OR free-text. When a path
is passed and the file exists, the full story text drives the query.
Otherwise the argument is treated as the query itself.

Options:

- `--story <path_or_text>`: Required. Story file or free text.
- `--map <path>`: Index path. Default:
  `sdlc-studio/.local/repo-map.json`.
- `--top <n>`: Number of results. Default: 15.
- `--format plain|json`: Output format. Default: plain.

Plain output format:

```text
  15.50  in=7    src/lib/auth/client.ts  [auth, client, login, email]
  11.00  in=4    src/db/users.ts         [users, login, email]
   8.50  in=2    src/api/auth.ts         [auth, login]
```

Columns: score, in_degree, path, matched tokens (truncated to first 5).

## Scoring {#repo-map-scoring}

Files are scored against a tokenised query:

| Component | Weight | Notes |
| --- | --- | --- |
| Symbol name match | 3.0 per match | Matches class, function, interface, struct names |
| Path token match | 2.0 per match | Matches directory segments and file stem |
| In-degree bonus | 0.5 per incoming reference | Only applied when at least one content token matched |

Tokens are case-insensitive, split on CamelCase and snake_case
boundaries, minimum 3 characters, with a short stopword list that
strips `test`, `class`, `function`, `api`, `ui`, `the`, `and`, etc.

Files with zero matched tokens score 0 regardless of in-degree. This
prevents hub files from polluting every query result – a file has to
be content-relevant before the hub bonus kicks in.

## Limits and Falsehoods {#repo-map-limits}

The repo map is a regex indexer with a Python AST special case. It is
intentionally shallow. What it does NOT do:

- **No type resolution.** `Foo` in file A and `Foo` in file B are
  treated as the same symbol. A real LSP would tell them apart; the
  repo map will not.
- **No macro or decorator expansion.** A class created via
  `@dataclass` is captured; a class created via a metaclass or a
  template may not be.
- **No dependency resolution.** Imports are matched by basename
  against known files. `import foo` matches any file whose stem is
  `foo`, which can cross-link unrelated packages. The in-degree
  heuristic tolerates this noise but does not eliminate it.
- **No call graph.** The in-degree score approximates module-level
  references, not function-level. A file imported twice by ten other
  files scores the same as a file imported once by ten other files.
- **No comments or docstring indexing.** Only declared symbol names
  are indexed. A well-documented function named `do_thing` will only
  match the tokens "do" and "thing", not the words in its docstring.

These limits are deliberate: the alternative is a language-server
integration per language, which is a project in itself. The repo map
is correct most of the time, fast always, and cheap to rebuild.

**When results are wrong**, the fix is usually one of:

1. Rebuild the index (it may be stale)
2. Rephrase the story description to use concrete symbol names
3. Pass `--top 25` to widen the candidate set
4. Manually augment the `READ THESE FILES FIRST` list after reviewing
   query output

## Integration {#repo-map-integration}

**Agent Prompt Template (`reference-agent-prompt-template.md#agent-prompt-template`):**
Run `repo_map.py query` against the story file before populating
`READ THESE FILES FIRST`. Use the top 5-10 results as the starting
file set; prune obvious false positives; add files the indexer
missed.

**Code Plan (`reference-code.md#code-plan-workflow`):** Step 6a in
the code plan workflow runs `repo_map.py build` if the index is
older than 1 hour, then `repo_map.py query` to seed the initial
file list for the plan. The plan author reviews the result before
the Three Amigos consultation.

**Agentic Lessons (`reference-agentic-lessons.md`):** Under "Agent
Prompts", the lesson "READ THESE FILES FIRST must not come from
memory" is now enforced by the repo map workflow.

**Not integrated:** The repo map is advisory. `reconcile`, `review`,
`story create`, and `cr action` do not consult it. They operate on
existing artefacts where a file list is already committed.

## Troubleshooting {#repo-map-trouble}

**Empty results:**

- Check the index exists: `python3 .../repo_map.py stats`
- Check the query has concrete tokens (not just generic words)
- Widen with `--top 25`
- Rebuild if the codebase has changed

**Too many false positives:**

- Narrow with `--top 5`
- Use a more specific query (include an expected class name)
- Review the `matched` column to see which tokens hit

**Index build fails:**

- Check `--root` is a real directory
- Check `.local/` is writable
- Run without `--out` to see errors to stderr
- Pass `--ignore` for any pathological directory (generated code,
  vendored third-party trees)

## See Also

- `scripts/repo_map.py` - The implementation
- `scripts/README.md` - Scripts directory conventions
- `reference-agent-prompt-template.md#agent-prompt-template` - Primary consumer
- `reference-code.md#code-plan-workflow` - Secondary consumer
- `help/repo-map.md` - User-facing help
- `reference-agentic-lessons.md` - Lessons that motivated this feature
