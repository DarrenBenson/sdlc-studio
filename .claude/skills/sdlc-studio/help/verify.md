<!-- Load when: user runs /sdlc-studio reconcile --verify or asks about executable acceptance criteria -->
<!-- Dependencies: reference-verify.md, reference-reconcile.md, scripts/verify_ac.py -->

# /sdlc-studio reconcile --verify - Help

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Check our acceptance criteria actually pass" | `/sdlc-studio reconcile --verify` |
| "Show me what to expect first, do not change anything" | `/sdlc-studio reconcile --verify --dry-run` |
| "Just verify the login story" | `/sdlc-studio reconcile --verify --story US0001` |
| "What is failing right now?" | `/sdlc-studio reconcile --verify report` |
| "Give me the verification results as JSON" | `/sdlc-studio reconcile --verify report --format json` |

> **Source of truth:** `reference-verify.md` - Full design, DSL, report format

Execute acceptance-criterion verifiers across story files and update
each AC's `Verified:` state in place. Replaces manual checkbox ticks
with mechanical, repeatable verification against the live codebase.

## Quick Reference

```bash
/sdlc-studio reconcile --verify                       # All stories, apply mode
/sdlc-studio reconcile --verify --dry-run             # Preview, no writes
/sdlc-studio reconcile --verify --story US0001        # Single story
/sdlc-studio reconcile --verify --ids US0001,US0003   # Just these stories, one process
/sdlc-studio reconcile --verify --worklist tranche.md # The ids a tranche file names
/sdlc-studio reconcile --verify --from-run            # The open run's approved batch
/sdlc-studio reconcile --verify --scope verify        # Reconcile scoped to verify
/sdlc-studio reconcile --verify --timeout 300         # Raise per-verifier timeout
/sdlc-studio reconcile --verify report                # Print the latest report
/sdlc-studio reconcile --verify report --format json  # JSON report
```

## Prerequisites

- Python 3.10 or later
- Stories with `- **Verify:** <expression>` lines on at least some ACs
- The tools referenced by the verifiers on PATH (`pytest`, `jest`,
  `rg`, `curl`, `jq`, etc.)
- A writable `sdlc-studio/.local/` directory for the report

## Actions

### run

Walks stories, runs verifiers, updates `Verified:` state in place,
writes the report.

**What happens:**

1. Resolves `--dir` (default `sdlc-studio/stories`) or `--story`
2. For each story file, parses AC blocks with their optional
   `Verify:` and `Verified:` lines
3. For each AC with a `Verify:` line, builds a subprocess command
   from the DSL prefix and runs it with `cwd=--repo-root`
4. Classifies the result: passed (verifier exit 0), failed (non-zero),
   manual (no `Verify:` line)
5. Updates story files in place unless `--dry-run`:
   - passing AC whose `Verified:` was missing gets a new line
   - passing AC whose `Verified:` was `no` or `stale` gets upgraded
   - failing AC whose `Verified:` was `yes` gets downgraded
6. Writes `sdlc-studio/.local/verify-report.json`
7. Exit code: 0 if all ACs pass or are manual, 1 if any failed

**Usage:**

```text
/sdlc-studio reconcile --verify
/sdlc-studio reconcile --verify --story US0001 --dry-run
/sdlc-studio reconcile --verify --timeout 300
```

**Output example:**

```text
[APL] US0001-login.md: ac=5 pass=4 fail=1 manual=0 changes=2
        FAIL AC4: pytest tests/test_auth.py::test_locked_account
          | AssertionError: expected 423, got 200
[APL] US0002-logout.md: ac=3 pass=3 fail=0 manual=0 changes=0
wrote sdlc-studio/.local/verify-report.json
```

The `[APL]` prefix means apply mode; `[DRY]` means dry run.

**Scoping the run to a batch.** A whole-workspace run re-executes every acceptance
criterion in the project, which on a large workspace costs minutes the sprint did not
need to spend. The selectors are mutually exclusive - one of `--story`, `--id`, `--ids`,
`--worklist` or `--from-run`:

```text
--ids US0001,US0003     explicit list; repeatable (--ids US0001 --ids US0003)
--worklist tranche.md   one id per line; bullets and `#` comments tolerated
--from-run              the story units of the open run's approved batch
```

Every form runs in ONE process. An id that resolves to no story file is an error (exit 2)
naming the id, never a skip a completion gate would read as green; `--from-run` with no run
open refuses rather than falling back to the whole workspace. Non-story ids in a worklist or
a run batch are dropped and reported. Scoped runs MERGE into the report, so out-of-scope
verdicts (and their freshness fields) survive untouched.

### report

Prints the latest verification report in text or JSON. Reads
`sdlc-studio/.local/verify-report.json`.

**Usage:**

```text
/sdlc-studio reconcile --verify report
/sdlc-studio reconcile --verify report --format json
```

**Output example:**

```text
generated_at: 2026-04-15T12:34:56Z
US0001-login: ac=5 pass=4 fail=1 manual=0
  FAIL AC4: pytest tests/test_auth.py::test_locked_account
US0002-logout: ac=3 pass=3 fail=0 manual=0
total: pass=7 fail=1 manual=0
```

## Arguments

### run

| Flag | Effect | Default |
| --- | --- | --- |
| `--dir <path>` | Stories directory | sdlc-studio/stories |
| `--story <path>` | Single story file (overrides `--dir`) | none |
| `--id <id>` | Single story by id, resolved under `--dir` | none |
| `--ids <a,b>` | Scope to these story ids (comma-separated, repeatable) | none |
| `--worklist <path>` | Scope to the ids a tranche file names | none |
| `--from-run` | Scope to the open run's approved batch | false |
| `--dry-run` | Do not modify story files | false |
| `--timeout <n>` | Per-verifier timeout in seconds | 120 |
| `--report <path>` | Report output path | sdlc-studio/.local/verify-report.json |
| `--repo-root <path>` | Cwd for verifier commands | `.` |

### report

| Flag | Effect | Default |
| --- | --- | --- |
| `--report <path>` | Report input path | sdlc-studio/.local/verify-report.json |
| `--format text\|json` | Output format | text |

## Writing a Verifier

Attach a `- **Verify:**` bullet to any AC in a story file. The first
token is a type prefix; the rest is interpreted in that type's
semantics. Examples:

```markdown
### AC1: Happy path email login
- **Given** a registered account
- **When** the user submits valid credentials
- **Then** they are redirected to /dashboard
- **Verify:** pytest tests/unit/auth/test_login.py::test_email_happy
```

Supported prefixes: `pytest`, `jest`, `vitest`, `go`, `file`, `grep`,
`http`, `shell`. Anything unrecognised falls back to `shell`. See
`reference-verify.md#verify-dsl` for the full table and examples.

## Examples

**Preview verification on one story without writing:**

```text
/sdlc-studio reconcile --verify --story US0017 --dry-run
```

**Verify every story after a big refactor:**

```text
/sdlc-studio reconcile --verify
```

**Scope a reconcile run to only verification (skip index/drift fixes):**

```text
/sdlc-studio reconcile --scope verify
```

**Check what's failing right now:**

```text
/sdlc-studio reconcile --verify report
```

## Related Commands

- `/sdlc-studio reconcile` - Full drift reconciliation across stories,
  epics, PRD, CRs, indexes, and checkboxes
- `/sdlc-studio story create` - Generates best-effort `Verify:` lines
  per AC based on story type

## See Also

- `reference-verify.md` - Full design, DSL table, gated completion
- `reference-reconcile.md#verify-scope` - How reconcile invokes verify_ac
- `reference-outputs.md#story-completion-cascade` - The require_ac_verification gate
- `scripts/verify_ac.py` - The implementation
