# BG0462: The version guard's discovery test cannot tell discovery from the hardcoded fallback that seeds the same two paths, and the gate swallows the UNVERIFIABLE notes it exists to print

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** tools/tests/test_check_versions.py, tools/check_versions.py, .githooks/pre-commit
> **Evidence:** Independent adversarial review of RUN-01KYTKA1 tranche A (QA seat, isolated worktree, 29 mutants applied, 6 survived). US0452=REJECT, US0454=REJECT, US0453=APPROVE.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0452's title is that the version guard reaches every authoritative home "discovered rather than hand-enumerated". Its verifier asserts only that `trd.md` and `tsd.md` appear in `discover_spec_homes()` - and those two paths are ALSO seeded by the hardcoded `SPEC_FILES` fallback, unioned in immediately afterwards. The test therefore passed with discovery entirely dead AND with the hardcoded list stripped: it cannot tell the two redundant sources apart, which is the one distinction the story is about. It also never calls `main()`, so AC1's "names each one that disagrees" is exercised nowhere.

US0454 AC2 says an absent measurement "says so plainly". It does, in the library - and the gate throws it away. The pre-commit `run()` helper captures the lane's output with `2>&1` into a variable and, on a zero exit, prints only `ok <key>`. The two UNVERIFIABLE notes `check_spec_claims.py` emits for the TSD's markers are discarded, and the developer sees a bare `ok spec-claims`. Executed: the lane exits 0, two UNVERIFIABLE lines are captured, zero are displayed. AC2's guarantee holds in the only place nobody is reading and fails in the only place anybody is.

The module docstring compounds it, still claiming the guard "extracts the version by structure from exactly five places - never by repo-wide grep". Executed, it checks 7 homes after reading the head of 2,448 tracked markdown files, and never mentions discovery at all - in a batch about spec truth.

## Steps to Reproduce

```text
mutant M2: discovery neutered (homes.append(rel) -> pass)
  -> SURVIVED US0452 AC1's own verifier, in isolation
mutant M3: the hardcoded SPEC_FILES seed stripped
  -> SURVIVED the same verifier
  (both paths appear via the other source, so neither absence is visible)

pre-commit spec-claims lane, executed:
  lane exit code        : 0
  UNVERIFIABLE captured : 2
  UNVERIFIABLE displayed: 0
  operator sees         : ok spec-claims

check_versions docstring: "exactly five places - never by repo-wide grep"
  actual: 7 homes, after reading the head of 2448 tracked .md files
```

## Proposed Fix

Assert a home that is NOT in `SPEC_FILES`, so the assertion can only be satisfied by discovery, and call `main()` so the disagreement-naming half of AC1 is exercised.

The gate must surface a lane's UNVERIFIABLE notes on a zero exit. A note whose whole purpose is to say "this could not be checked" is worth nothing if the only caller discards it when the check passes - and passing is exactly when it is emitted.

Correct the docstring to the shipped behaviour, including discovery.

## Acceptance Criteria

- [ ] US0452 AC1's verifier asserts a discovered home that `SPEC_FILES` does not contain, so neutering discovery reddens it, and stripping the hardcoded seed reddens it too - each verified by applying its mutant
- [ ] The verifier calls `main()` and asserts it NAMES the home that disagrees, rather than asserting only membership of a list
- [ ] A lane's UNVERIFIABLE notes reach the operator on a zero exit rather than being discarded by the hook's output capture
- [ ] `check_versions.py`'s docstring states the shipped behaviour: the number of homes it actually checks, and that discovery is how it finds them

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
