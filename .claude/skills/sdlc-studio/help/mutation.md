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
2. Confirms the baseline is green (a red baseline cannot judge - every mutation records
   `error`, never a fake kill).
3. Applies one mutation at a time, re-runs `--test`, restores the original bytes, and
   verdicts it killed / survived / error.
4. Writes `sdlc-studio/.local/mutation-report.json`; the release gate's `mutation` lane
   surfaces it (advisory in v1; absent report reads not-run, never PASS).

## Reading the verdicts

- **killed** - the test failed against the mutant: it pins the behaviour. Only viable
  mutants can kill: a Python mutant is compile-checked first, and one that cannot parse
  records **unviable** (evidence of nothing - any suite, however vacuous, fails on it).
- **survived** - the test stayed green over broken code: a finding. Triage note: a
  code-shaped line inside a docstring can mutate without changing behaviour and
  false-survive; check the reported line before acting.
- **error** - the runner itself broke (missing command, timeout, red baseline); never
  counted as a kill.
- The report records the **git rev** it ran at; the gate's mutation lane reports a
  report from another rev as STALE rather than PASS.

## Honest degrade

- A file/class the profiles cannot mutate is listed **un-checked**, never passed.
- `--max-mutations N` (default `quality.mutation_max`, else 25) bounds cost; enumerations
  beyond the ceiling are counted as **truncated** - un-checked coverage, not clean.
- Exit is non-zero on any survivor or error.

## See Also

- `reference-test-best-practices.md#mutation-check` - the discipline this enforces
- `reference-scripts.md` - the full catalogue entry
- `help/verify.md` - the passing half of the claim
