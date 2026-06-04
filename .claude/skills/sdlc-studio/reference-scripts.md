# SDLC Studio Reference - Skill Internal Scripts

Runtime helpers that live at `.claude/skills/sdlc-studio/scripts/` and
are invoked by workflow reference files. Claude calls these; users do
not.

<!-- Load when: a reference file instructs invoking a script in scripts/ -->

## Reading Guide

| Section | When to Read |
| --- | --- |
| Rationale | When deciding whether a new helper belongs in scripts/ |
| Invocation | When a reference file needs to call a script |
| Contract | When writing or modifying a script |
| Catalogue | When finding an existing helper before writing a new one |

## Rationale {#scripts-rationale}

SDLC Studio was Claude-native through v1.5.0: every workflow was a
markdown instruction that Claude executed using built-in tools (Read,
Grep, Bash, Edit). v1.6.0 introduces three capabilities that need
deterministic computation:

1. **AST repository indexing** (`repo_map.py`) – reinventing a ranked
   file index every session wastes tokens and drifts.
2. **AC verifier execution** (`verify_ac.py`) – running pytest, curl,
   or shell assertions at scale needs a single entry point that
   parses results and updates story files atomically.
3. **GitHub issue sync** (`github_sync.py`) – diffing local CR/Story
   files against GitHub Issues and writing back needs idempotent
   logic that a script can unit-test.

For everything else (reading files, walking directories, simple
transforms) Claude's built-in tools are still the right answer. The
scripts directory is for computation that benefits from being written
once and tested.

## Invocation {#scripts-invocation}

Reference files call scripts via Bash:

```bash
python3 .claude/skills/sdlc-studio/scripts/repo_map.py query \
  --story sdlc-studio/stories/US0001-user-login.md --top 10
```

Always use the absolute path from repo root. Never `cd` into the
scripts directory. Always pass `--dry-run` first when the workflow
explicitly supports it.

## Contract {#scripts-contract}

Every script in `scripts/`:

1. Starts with `#!/usr/bin/env python3` and is executable
2. Uses `argparse` subcommands for commands (e.g. `repo_map.py build`)
3. Supports `--help` on every subcommand
4. Exits non-zero on any failure that should halt the workflow
5. Never mutates files outside `sdlc-studio/.local/` or the files
   passed on the command line
6. Never fetches network resources except the explicit GitHub CLI
   wrapper, and even then only via the `gh` tool (no token handling)
7. Prints plain text to stdout by default, with `--format json` where
   machine-parseable output matters
8. Has unit tests under `scripts/tests/test_<script>.py`

See `best-practices/script.md` for the shared style rules (shebang,
error handling, CLI flags over config files for small tools).

## Catalogue {#scripts-catalogue}

### `repo_map.py`

Pure-Python repository indexer. Produces
`sdlc-studio/.local/repo-map.json` with per-file symbol lists, imports,
and an in-degree score. Queried by the Agent Prompt Template and
`code plan` workflow to derive `READ THESE FILES FIRST` lists.

- `build`: walk the repo and write the index
- `query`: rank files against a story or free-text query
- `stats`: print index size and top-10 hub files

Full workflow: `reference-repo-map.md`. User-facing help:
`help/repo-map.md`.

### `verify_ac.py`

Executes AC verifiers defined in story files and updates each AC's
`Verified:` line. Drives `/sdlc-studio reconcile --verify`.

- `run`: walk stories, run verifiers, write report
- `report`: print the latest verification report

Full workflow: `reference-verify.md`. User-facing help:
`help/verify.md`.

### `github_sync.py`

Two-way sync between local CR/Story/Epic files and GitHub Issues via
the `gh` CLI.

- `pull`: fetch issues with `sdlc:*` labels and create local files
- `push`: create or update issues from local files
- `cascade`: walk merged PRs and trigger Story Completion Cascades
- `state`: print sync state

Full workflow: `reference-github-sync.md`. User-facing help:
`help/github-sync.md`.

## See Also

- `best-practices/script.md` - Style rules for shell and Python scripts
- `scripts/README.md` - Directory overview for contributors
- `reference-repo-map.md`, `reference-verify.md`, `reference-github-sync.md` - Consumer workflows
