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
4. Writes `sdlc-studio/.local/mutation-report.json`; the release gate's `mutation` lane
   surfaces it (advisory in v1; absent report reads not-run, never PASS).

## Reading the verdicts

- **killed** - the test failed against the mutant: it pins the behaviour. Only viable
  mutants can kill: a Python mutant is compile-checked first, and one that cannot parse
  records **unviable** (evidence of nothing - any suite, however vacuous, fails on it).
- **survived** - the test stayed green over broken code: a finding. Triage note: a
  code-shaped line inside a docstring can mutate without changing behaviour and
  false-survive on non-Python files; Python string interiors are excluded automatically.
- **error** - the runner itself broke on a mutant (missing command, timeout); never counted
  as a kill. (A red baseline does not reach this state - it refuses the whole run up front.)
- The report records the **git rev** and a **content hash per target**; the gate's
  mutation lane reports STALE on a rev change OR any target edited since the run -
  a dirty tree cannot ride an old green report.

## Honest degrade

- A file/class the profiles cannot mutate is listed **un-checked**, never passed.
- `--max-mutations N` (default `quality.mutation_max`, else 25) bounds cost; the budget
  distributes round-robin with files as the fast axis (every file gets coverage before
  any class repeats), and enumerations beyond the ceiling are counted as **truncated** -
  un-checked coverage, not clean.
- Lines inside docstrings/multi-line strings are not enumerated (they mutate nothing
  and would false-survive); a file the tokeniser cannot parse has that exclusion
  skipped and NOTED in the un-checked list.
- Exit is non-zero on any survivor or error.

## See Also

- `reference-test-best-practices.md#mutation-check` - the discipline this enforces
- `reference-scripts.md` - the full catalogue entry
- `help/verify.md` - the passing half of the claim
