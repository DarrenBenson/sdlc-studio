<!-- Load when: user runs /sdlc-studio repo map build|query|stats or asks about the repo indexer -->
<!-- Dependencies: reference-repo-map.md, scripts/repo_map.py -->

# /sdlc-studio repo map - Help

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Index the codebase so you know your way around" | `/sdlc-studio repo map build` |
| "Which files matter for the login story?" | `/sdlc-studio repo map query --story US0001` |
| "What handles email notifications in here?" | `/sdlc-studio repo map query --story "email notifications"` |
| "Show me the most-used files in this project" | `/sdlc-studio repo map stats` |
| "Re-index, we just did a big refactor" | `/sdlc-studio repo map build` |

> **Source of truth:** `reference-repo-map.md` - Detailed workflow and design

Pure-Python repository indexer that ranks source files by relevance
to a story description. Used to seed `READ THESE FILES FIRST` lists
in the Agent Prompt Template and to pre-populate candidate file lists
during `code plan`.

## Quick Reference

```bash
/sdlc-studio repo map build                          # Build the index
/sdlc-studio repo map build --ignore vendor          # Skip an extra directory
/sdlc-studio repo map query --story US0001           # Rank files for a story
/sdlc-studio repo map query --story "auth flow"      # Free-text query
/sdlc-studio repo map query --story US0001 --top 25  # Widen the result set
/sdlc-studio repo map stats                          # Index size and top hubs
```

Each slash command maps to a `python3 "$CLAUDE_SKILL_DIR/scripts/repo_map.py" <subcommand>`
invocation (see `reference-scripts.md#skill-dir`). Claude runs the
script; users see the output.

## Prerequisites

- Python 3.10 or later (standard on Ubuntu 24.04 and macOS 14+)
- An `sdlc-studio/.local/` directory writable for the index output
- A source repository with files in supported languages: Python,
  TypeScript, JavaScript, Go, Rust, Java, Kotlin, C#, Ruby, PHP,
  Swift

## Actions

### build

Walk the repository, extract symbols and imports, write the index.

**What happens:**

1. Resolves `--root` (default: current directory) to an absolute path
2. Enumerates source files matching supported extensions, skipping
   `.git`, `node_modules`, `__pycache__`, and 20+ other noise dirs
3. Parses each file: Python via stdlib `ast`, other languages via
   regex
4. Computes a per-file `in_degree` score from the import graph
5. Writes JSON to `sdlc-studio/.local/repo-map.json`
6. Prints `indexed <n> files in <t>s`

**Usage:**

```text
/sdlc-studio repo map build
/sdlc-studio repo map build --root . --out sdlc-studio/.local/repo-map.json
/sdlc-studio repo map build --ignore vendor --ignore generated
```

**Output example:**

```text
indexed 284 files in 1.42s -> sdlc-studio/.local/repo-map.json
```

### query

Rank files by relevance to a story or free-text description.

**What happens:**

1. Loads the index from `--map` (default
   `sdlc-studio/.local/repo-map.json`)
2. If `--story` is a path to an existing file, reads it; otherwise
   treats `--story` as free text
3. Tokenises the text, splitting CamelCase and snake_case, removing
   stopwords
4. Scores every indexed file by symbol-token matches (3.0 each),
   path-token matches (2.0 each), plus an in-degree bonus (0.5 per
   incoming reference) for files that matched on content
5. Prints the top-N results or emits JSON

**Usage:**

```text
/sdlc-studio repo map query --story sdlc-studio/stories/US0001-user-login.md
/sdlc-studio repo map query --story "user authentication email flow" --top 5
/sdlc-studio repo map query --story US0001 --format json
```

**Output example (plain):**

```text
  15.50  in=7    src/lib/auth/client.ts  [auth, client, login, email]
  11.00  in=4    src/db/users.ts         [users, login, email]
   8.50  in=2    src/api/auth.ts         [auth, login]
```

Columns: score, in_degree, path, matched tokens (first 5).

### stats

Print index size, per-language file counts, and the top-10 hub files
by incoming reference count.

**Usage:**

```text
/sdlc-studio repo map stats
/sdlc-studio repo map stats --map /custom/path/repo-map.json
```

**Output example:**

```text
generated_at: 2026-04-15T10:22:14Z
root:         /home/darren/projects/my-app
files:        284
by language:
  typescript    142
  python         61
  go             34
  rust           20
  javascript     27
top hubs (by in_degree):
    42  src/lib/schema.ts
    35  src/db/client.ts
    28  src/api/router.ts
```

## Arguments

### build

| Flag | Effect | Default |
| --- | --- | --- |
| `--root <path>` | Repository root to index | current directory |
| `--out <path>` | Output JSON path | sdlc-studio/.local/repo-map.json |
| `--ignore <name>` | Extra directory to skip (repeatable) | none |

### query

| Flag | Effect | Default |
| --- | --- | --- |
| `--story <path_or_text>` | Story file path or free-text query | required |
| `--map <path>` | Repo map JSON path | sdlc-studio/.local/repo-map.json |
| `--top <n>` | Number of results | 15 |
| `--format plain\|json` | Output format | plain |

### stats

| Flag | Effect | Default |
| --- | --- | --- |
| `--map <path>` | Repo map JSON path | sdlc-studio/.local/repo-map.json |

## Examples

**Rebuild after a big refactor:**

```text
/sdlc-studio repo map build
```

**Seed the Agent Prompt Template for a story:**

```text
/sdlc-studio repo map query --story sdlc-studio/stories/US0042-backup-flow.md --top 10
```

**Free-text query during brainstorming:**

```text
/sdlc-studio repo map query --story "how does the current notification system work"
```

**Find the project's hub files:**

```text
/sdlc-studio repo map stats
```

## Related Commands

- `/sdlc-studio code plan --story US0001` - Consults the repo map when
  drafting the initial file list
- `/sdlc-studio epic implement --epic EP0001 --agentic` - Consults
  the repo map to populate `READ THESE FILES FIRST` for each story
  prompt

## See Also

- `reference-repo-map.md` - Full design, scoring, and limits
- `reference-agent-prompt-template.md#agent-prompt-template` - Primary consumer
- `reference-code.md#code-plan-workflow` - Secondary consumer
- `scripts/repo_map.py` - The implementation
