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
verdicts (and their freshness fields) survive untouched, and a shared story gets the same
verdict it would have got from the whole-workspace run.

`--fresh` rebuilds the report from the run alone. Combined with a scope that would delete
every verdict outside it, so the combination is refused (exit 2, nothing written): drop the
scope to rebuild the whole report, or drop `--fresh` so the scoped run merges into it.

### run --coverage

Measure which of a unit's OWN added lines its OWN verifiers executed, after the run:

```bash
python3 <skill>/scripts/verify_ac.py run --id US0042 --coverage            # the unit's run supplies the base ref
python3 <skill>/scripts/verify_ac.py run --id US0042 --coverage --base abc1234   # no run names it
```

The base ref is the one recorded by the run whose approved batch names the unit, open or
closed; with none, `--base <ref>` is required and its absence refuses. A line is the unit's
when a commit between that ref and HEAD names the unit in its subject or on a `Refs:` line
(one per line as the commit-msg hook writes them, or the older comma form), or when it is
still uncommitted; a cluster-mate's commit in a shared file is not this unit's. Coverage is
collected from the unit's own `pytest` selectors alone, on `SDLC_COVERAGE_PYTHON` when set
(else the current interpreter), following the child interpreters they spawn. A `shell`,
`grep`, `eval` or `http` verifier is listed `not traced`; a Python file with no traced
verifier is `not measured`; a non-Python file is `not measurable`. Exit 1 on any uncovered
added line; exit 2 naming the dependency when the module is missing (`coverage: not measured -
the coverage module is absent`), when it is older than 7.10 (`... is below the floor 7.10 ...`),
or when a verifier outruns the timeout under coverage. The `--report` JSON gains a `coverage` key carrying the
per-file uncovered lines, the base ref and a hash over the unit's Affects, so a gate can tell
a stale report from a current one. Data files live under `sdlc-studio/.local/coverage/`.

### coverage rule

Rule one uncovered added line equivalent, inside the artefact:

```bash
python3 <skill>/scripts/verify_ac.py coverage rule --id US0042 --file src/thing.py --line 88 \
    --reason "a defensive arm no fixture can reach without faking the OS"
```

The ruling is a row in the unit's own `## Coverage Rulings` table - file, line, the file's
content hash, reason, author, date - tracked with the artefact, never in `.local/`. A reason
shorter than the floor `mutation.py retract` holds a withdrawal to is refused. The terminal
transition subtracts live rulings from the uncovered lines; `verify_ac.py depth --write` is what
writes `lines ruled N` into the derived half of `Verification depth`, and the transition never
writes that field itself. A ruling made on bytes the file no longer has is STALE: it asserts
nothing about the tree in front of you, so it is reported in every mode and blocks nothing -
whatever it once excused is either executed now or still uncovered and counted as such.
`coverage withdraw --id <unit> --file <path> --line <n> --reason <why>` retracts one on the
record: the row stays in the table, carrying both reasons, and counts for nothing after.

### testplan probe

Asks, of every criterion in one unit, whether it CAN FAIL as written - the question nothing else
in the toolchain asks:

```bash
python3 <skill>/scripts/verify_ac.py testplan probe --unit BG0123
```

It runs each criterion's `Verify:` selector against the tree as it is and classifies the answer.
A criterion that already PASSES is the finding: it states what the tree already does, so
delivering it would prove nothing, and the command exits non-zero. So is one whose every
selected test is skipped (`never-fails`), and one whose answer the runner could not be trusted
to give (`unreadable` - an invalid selector, a timeout, an absent runner, or a `grep` that
exited 2 because it could not run at all). Everything else is a state a plan is allowed to be
in: `red` is what a plan SHOULD look like, `not-yet-written` is the ordinary state before the
test exists, `manual` and `unspecified` have nothing to run, `delivered` is a green criterion on
a unit whose commits already do the work, and `pinned` is a finding carrying a live ruling.

A `shell`, `eval` or `http` verifier is named `not-probed` and NOTHING is executed for it: a
plan-time check must not run shell somebody else authored into an artefact.

`sprint plan` runs the same probe over a whole batch - see `review.plan_falsifiability` in the
[configuration reference](../reference-config.md#plan-falsifiability).

### testplan rule / testplan withdraw

Record the decision to plan over a criterion the probe named, so the exemption is on the record
rather than in somebody's head:

```bash
python3 <skill>/scripts/verify_ac.py testplan rule --unit BG0123 --criterion AC2 \
    --reason "the behaviour shipped in an earlier unit and this row pins the regression" \
    --author "engineering seat"
```

All four are required; a reason shorter than the floor is refused, because a one-character
reason is not a decision anybody can review. The row lands in
`sdlc-studio/reviews/plan-rulings.md` - tracked beside the other review records, not in
gitignored `.local/`, because a ruling is evidence and evidence nobody else can read is evidence
only its author has.

The ruling is pinned to a digest over the criterion's TITLE and its SELECTOR together. Rewrite
either and the ruling is reported STALE with its reason rather than quietly continuing to
excuse a criterion that now says something else. A criterion carrying a live, non-stale ruling
is `pinned`: reported, never refused.

```bash
python3 <skill>/scripts/verify_ac.py testplan withdraw --unit BG0123 --criterion AC2 \
    --reason "the criterion was rewritten and can fail now"
```

A withdrawal MARKS the row in place rather than deleting it, carrying both reasons, and the
criterion is a finding again. A withdrawal naming no live row is refused rather than exiting 0,
which would leave the author believing a pin was lifted that is still standing.

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
| `--fresh` | Rebuild the report from this run only (refused with a scope) | false |
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

## The duplicate-verifier ratchet

Two ACs sharing a Verify selector cannot both discriminate: a regression in either fails both,
and neither tells you which broke. `lint --ratchet` refuses any shared selector the baseline does
not already record.

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/verify_ac.py" lint --ratchet --bugs
```

- **`--bugs` is load-bearing.** The scan defaults to stories, and a shared selector parked in a
  bug is precisely where nobody was looking.
- **The tolerated set may only shrink.** A recorded group that is no longer duplicated is refused
  too, or a fixed entry could be spent again to admit a new one and the ratchet would only loosen.
- **A tolerated entry names exactly the ACs that share the selector**, plus a reason a human
  wrote. If the selector later spreads to more ACs, the entry no longer describes the group
  anybody tolerated and the lane refuses it. Only a story or a bug may be named, since only those
  carry ACs.
- **`--stamp` records the current groups with an EMPTY reason and exits non-zero**, so a stamp
  cannot manufacture an exemption nobody decided on. Fill each reason in by hand.

Baseline: `sdlc-studio/.verify-lint-baseline.json`. An absent, unreadable or stale baseline is
reported as its own state - none of them reads as a clean scan.

## See Also

- `reference-verify.md` - Full design, DSL table, gated completion
- `reference-reconcile.md#verify-scope` - How reconcile invokes verify_ac
- `reference-outputs.md#story-completion-cascade` - The require_ac_verification gate
- `scripts/verify_ac.py` - The implementation
