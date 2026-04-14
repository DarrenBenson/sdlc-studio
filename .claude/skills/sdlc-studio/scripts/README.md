# SDLC Studio Scripts

Runtime helpers invoked by SDLC Studio workflows. These scripts are
skill internals. End users do not call them directly; Claude invokes
them on behalf of the reference-file workflows.

## Contents

| Script | Purpose | Reference |
| --- | --- | --- |
| `repo_map.py` | Pure-Python repository indexer. Ranks source files by relevance to a story description so the Agent Prompt Template can start from a derived file list instead of a hand-authored guess. | `reference-repo-map.md` |
| `verify_ac.py` | Executes acceptance-criteria verifiers and updates each AC's `Verified:` state in the story file. Drives `/sdlc-studio reconcile --verify`. | `reference-verify.md` |
| `github_sync.py` | Two-way sync between local CRs, Stories, Epics and GitHub Issues via the `gh` CLI. Handles pull, push, PR-merge cascade, and conflict reporting. | `reference-github-sync.md` |

## Conventions

Every script in this directory follows `../best-practices/script.md`:

- Shebang: `#!/usr/bin/env python3`
- Executable bit set
- `--help` on every subcommand
- Non-zero exit on failure
- CLI flags for configuration (no hard-coded paths)
- Pure stdlib unless a system tool is explicitly required (`gh`, `rg`)
- Unit tests in `scripts/tests/` runnable via `python3 -m unittest discover -s scripts/tests`

## Why scripts at all

The skill shipped no executable code through v1.5.0. Workflows were
entirely Claude-native. From v1.6.0 onward, three capabilities need
real computation (indexing, subprocess verification, HTTP sync) that
cannot be usefully reinvented in every Claude session. The scripts
directory captures that computation once, deterministically, with
tests. See `reference-scripts.md` for the design rationale.

## Tests

```bash
cd .claude/skills/sdlc-studio
python3 -m unittest discover -s scripts/tests
```

All tests must pass before a release is tagged.
