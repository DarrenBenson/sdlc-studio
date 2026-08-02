# BG0462: The version guard's discovery test cannot tell discovery from the hardcoded fallback that seeds the same two paths, and the gate swallows the UNVERIFIABLE notes it exists to print

> **Status:** Fixed
> **Verification depth:** functional + mutation (discovery deleted -> KILLED; the old verifier survived the same mutant)
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

### AC1: the assertion can only be satisfied by discovery

- **Given** a version-declaring markdown file that is NOT a member of `SPEC_FILES`
- **When** `discover_spec_homes` runs
- **Then** it is found, and the test asserts the fixture path is outside `SPEC_FILES` so the assertion cannot be satisfied by the unconditional union
- **Verify:** pytest tools/tests/test_check_versions.py::DiscoveryIsNotEnumerationTests::test_a_home_outside_the_enumeration_is_discovered
- **Verified:** yes (2026-08-02)

> **Mutation-verified.** Replacing the body with `return sorted(SPEC_FILES)` - discovery
> deleted entirely - KILLS this test. The original verifier asserted only that `trd.md` and
> `tsd.md` appear in the result, and both are unioned in unconditionally, so it survived that
> same mutant. Measured on this repo all three discovered homes are in `SPEC_FILES`, so the
> discriminating case had to be built as a fixture rather than found.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
