# SDLC Studio Scripts

Runtime helpers invoked by SDLC Studio workflows. These scripts are
skill internals. End users do not call them directly; Claude invokes
them on behalf of the reference-file workflows.

## Contents

| Script | Purpose | Reference |
| --- | --- | --- |
| `lib/sdlc_md.py` | Shared parsing/utility library (metadata fields, artifact IDs, AC blocks, timestamps, safe JSON, artifact-type and status-vocab tables). Imported by the other scripts; single source of truth for the markdown conventions. | `reference-scripts.md` |
| `repo_map.py` | Pure-Python repository indexer. Ranks source files by relevance to a story description so the Agent Prompt Template can start from a derived file list instead of a hand-authored guess. | `reference-repo-map.md` |
| `verify_ac.py` | Executes acceptance-criteria verifiers and updates each AC's `Verified:` state in the story file. Drives `/sdlc-studio reconcile --verify`. | `reference-verify.md` |
| `github_sync.py` | Two-way sync between local CRs, Stories, Epics and GitHub Issues via the `gh` CLI. Handles pull, push, PR-merge cascade, and conflict reporting. | `reference-github-sync.md` |
| `reconcile.py` | Read-only drift detection: builds the artifact-file census and reports where `_index.md` tables have drifted (status mismatch, missing/orphan rows, count drift). Emits JSON; Claude applies fixes and the judgement. | `reference-reconcile.md` |
| `status.py` | Four-pillar census (Requirements/Code/Tests/Reviews) plus the next-step hint, as JSON. Drives `/sdlc-studio status` and `hint`. | `help/status.md` |
| `validate.py` | Artifact-structure linter: ID format, Status drawn from the type vocabulary, title/metadata block, AC presence. | `reference-decisions.md` |
| `next_id.py` | Allocate the next free artifact ID for a type (local plus, with `--remote`, `origin/main`). | `reference-outputs.md` |
| `review_prep.py` | Deterministic inputs for the five-leg unified review: artifact staleness, persona usage, count/AC inputs. | `reference-review.md` |

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

The skill shipped no executable code through v1.5.0; every workflow was
Claude-native. The principle since: **determinism in scripts, judgement in
Claude.** Mechanical work - census, parsing, counting, drift detection,
validation, ID allocation - is computed once, deterministically, with tests,
so the model spends its tokens on judgement (design soundness, drift
adjudication, the five-leg review) rather than re-deriving state every
session. The read-only helpers (`reconcile`, `status`, `validate`,
`next_id`, `review_prep`) emit JSON that Claude consumes. See
`reference-scripts.md` for the design rationale and the script contract.

## Tests

```bash
cd .claude/skills/sdlc-studio
python3 -m unittest discover -s scripts/tests
```

All tests must pass before a release is tagged.
