<!--
Load when: /sdlc-studio mutation, code verify --mutation, or "can this test fail?"
Dependencies: SKILL.md (always loaded first)
Related: reference-test-best-practices.md#mutation-check, reference-scripts.md, help/verify.md
-->

# /sdlc-studio mutation - the executable mutation-check gate

## You can just ask

| Just say... | Runs |
| --- | --- |
| "Would these tests actually catch a break in target.py?" | `mutation.py run --files target.py --test "<suite>"` |
| "Mutation-check what this release changed" | `mutation.py run --since v3.3.0 --test "<suite>"` |
| "Mutation-check this story's surface" | `mutation.py run --story US0051 --test "<suite>"` |
| "Which of these tests assert nothing?" | `mutation.py prefilter --tests tests/*.py` |

`verify_ac` proves an AC's tests **pass**; this gate proves they can **fail**. It applies a
declared, bounded fault set to the surface, re-runs the tests per mutation, and reports
**killed** (good - the test pins the behaviour) vs **survived** (a finding - the test stayed
green over broken code).

## Quick Reference

```bash
python3 <skill>/scripts/mutation.py run --files src/loader.py --test "python3 -m unittest discover"
python3 <skill>/scripts/mutation.py run --since HEAD~1 --test "npm test"
python3 <skill>/scripts/mutation.py run --story US0051 --test "pytest -q"
python3 <skill>/scripts/mutation.py prefilter --tests tests/test_*.py
```

## What it does

1. Enumerates mutations over the surface from the declared fault classes -
   `invert-guard`, `stub-return-null`, `unset-delivered-field`, `no-op-mapper` - using
   per-language pattern profiles (`.py`, `.js`/`.ts`, `.go` invert-guard).
2. Confirms the baseline is green first. A red or broken baseline cannot judge anything, so
   the run **refuses** immediately - no mutant is applied, the report is marked `refused` with
   the remedy, and the exit is non-zero. (Running the mutants over red code would only produce
   a worthless all-`error` report a run could mistake for done.)
3. Applies one mutation at a time, re-runs `--test`, restores the original bytes, and
   verdicts it killed / survived / error. A kill (`TaskStop`/SIGTERM) or crash mid-mutant
   still restores via an atexit and SIGTERM handler, so a run never strands a mutant on disk.
   Against a SIGKILL those handlers never run, so the original bytes are also persisted to
   `sdlc-studio/.local/mutation-inflight.json` BEFORE each mutant lands: the next run
   restores from that sidecar first (reported as `recovered`), so a stranded mutant is
   never read back as the original. An unreadable sidecar refuses the run and names the
   git restore path.
4. Writes two files. `sdlc-studio/.local/mutation-report.json` is the **latest run** - every
   mutant's verdict, the git rev and a content hash per target - and is last-write-wins, so a
   per-unit run mid-sprint replaces the previous unit's.
   `sdlc-studio/.local/mutation-runs.json` is the **ledger**, the durable per-target half the
   gate lane reads as coverage (below). The gate's `mutation` lane surfaces both and is
   advisory in v1: it never changes the exit code, and an absent report reads not-run,
   never PASS.
5. Names what the survivors were measured against: the report and the text output carry
   the test files the command statically resolves to (`selected_tests`; UNRESOLVED when
   no file, directory or module token parses - never a guessed empty set), and a
   **WARNING** per test file that references a target module but sits outside that
   selection - the manufactured-survivor condition: a run scoped below the target's real
   coverage over-reports absence, so a survivor from a narrow run must be read against
   the recorded command (`test_cmd` in the JSON), not as proof of a missing test. The
   warning is advisory and never changes the exit code: a deliberately narrow run stays
   legal, and stays honest about what it covered. Two reading notes: selection is FILE
   granularity (`--ignore`/`--deselect` paths are honoured as unselected; a `-k` filter
   inside a selected file is invisible to it), and the reference check matches the target's
   module name as a bare word, so a file merely mentioning it can warn - a false warning
   costs reading time, never a verdict.

## Reading the verdicts

- **killed** - the test failed against the mutant: it pins the behaviour. Only viable
  mutants can kill: a Python mutant is compile-checked first, and one that cannot parse
  records **unviable** (evidence of nothing - any suite, however vacuous, fails on it).
- **survived** - the test stayed green over broken code: a finding. Triage note: a
  code-shaped line inside a docstring can mutate without changing behaviour and
  false-survive on non-Python files; Python string interiors are excluded automatically.
- **error** - the runner itself broke on a mutant (missing command, timeout); never counted
  as a kill. (A red baseline does not reach this state - it refuses the whole run up front.)
- The report records the **git rev** and a **content hash per target**, but neither is
  coverage: the hashes are written for every file *named* as a target, before any verdict
  exists, so a refused run records one for a file no mutant ever reached. They are read as a
  freshness stamp, and the rev attributes the survivor counts to the run that produced them.
  Per-file evidence is the ledger's.

## The ledger - what the gate lane reads

`sdlc-studio/.local/mutation-runs.json` accumulates evidence **per target**, so coverage is
judged file by file rather than from one whole-blob stamp that goes stale the moment any file
is committed.

- **One entry per target, keyed on that file's content hash at run time.** A later commit
  touching other files leaves the entry readable, which is what lets per-unit runs gathered
  during a build survive to the close.
- **A target is entered only when the test command returned a `killed` or `survived` verdict
  on it.** A target whose mutants were all unviable, all errored, or fell beyond the cost
  ceiling is absent, and so is every target of a refused run - a refusal applies no mutant, so
  no target has a verdict.
- **Bounded at 200 entries**, oldest out first, with a cumulative `dropped` total in the file
  and a note on the run's output, so truncation is counted rather than silent. Entries are one
  per target, so the ledger grows with the number of distinct files ever mutated, not with the
  number of runs. An unreadable ledger is replaced and says so (`reset`).
- **`measured` against `registered`.** A `measured` entry is a run that applied the mutant and
  observed the suite's answer. `mutation.py register --target F --mutant "..." --test "..."
  --verdict killed|survived|equivalent` records a mutant a builder applied **by hand**, so the
  per-unit practice (write a test, mutate the code it pins, see RED, restore) leaves a trace.
  Nothing re-runs anything, so that entry is a self-report and is reported as a claim, never as
  a measured run; a measured entry outranks a registered one on the same content. A run
  supersedes only its own kind, so it never deletes a hand-registered claim about the same file.
- Registrations accumulate into one entry per (target, content). That entry's `mutants` list is
  bounded at 100 with a `dropped_mutants` count, while its `summary` tallies are never
  truncated - what is dropped is the description, never the count.

### The per-file verdict

The lane judges the **changed surface** (mutatable non-test files with staged, unstaged or
untracked changes) when git can name it, and otherwise the files the ledger itself holds,
saying which of the two it read.

| Ledger state for the file | Verdict |
| --- | --- |
| A `measured` entry whose hash matches the file now | **covered** |
| No measured match, but a `registered` entry matches carrying `killed` or `survived` | **covered**, and named as a self-report |
| A `registered` entry matches carrying only `equivalent` | **uncovered**, named EQUIVALENT-ONLY: it says no test could have killed the mutant, which is a statement about the mutant, not about the suite |
| An entry exists, but no hash matches the file now (or none was recorded) | **STALE** |
| No entry for the file | **uncovered** |

Staleness is therefore per file: the file's bytes changed since the entry that covers it. A
self-reported **survivor** is reported as a finding - the builder's own test did not catch the
mutant they applied. With nothing in the ledger to judge, the lane degrades to the whole-report
checks, where a target the report hashed and edited since, or a report git rev that is not the
tree's HEAD, reads STALE. Either way the lane is advisory: it reports gaps and never refuses a
close.

## Honest degrade

- A file/class the profiles cannot mutate is listed **un-checked**, never passed.
- `--max-mutations N` (default `quality.mutation_max`, else 25) bounds cost; the budget
  distributes round-robin with files as the fast axis (every file gets coverage before
  any class repeats), and enumerations beyond the ceiling are counted as **truncated** -
  un-checked coverage, not clean.
- With `--since REF` the ceiling is spent on the **changed lines first**, and only the
  remainder reaches untouched code - otherwise a low ceiling on a large file samples
  peripheral helpers and reports a kill rate about code nobody edited. The report carries
  `diff_mutations` / `diff_applied` / `diff_covered`, and a run that could not reach every
  mutant on the diff says so rather than leaving it to be inferred from the truncation count.
- Lines inside docstrings/multi-line strings are not enumerated (they mutate nothing
  and would false-survive); a file the tokeniser cannot parse has that exclusion
  skipped and NOTED in the un-checked list.
- Exit is non-zero on any survivor or error.

## See Also

- `reference-test-best-practices.md#mutation-check` - the discipline this enforces
- `reference-scripts.md` - the full catalogue entry
- `help/verify.md` - the passing half of the claim
