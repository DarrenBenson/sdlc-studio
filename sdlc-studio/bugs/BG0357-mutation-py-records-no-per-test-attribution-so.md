# BG0357: mutation.py records no per-test attribution, so the prune-candidate consumer can never run

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, tools/test_census.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ closing review); agent; skill v5.0.0

## Summary

US0507 ships a consumer that nominates a test no mutation of its own module can kill. It requires each killed mutant to carry the test that killed it. mutation.py, this repository's only producer of mutation evidence, never emits that key, so the consumer takes its refusal branch against every real report. The refusal is loud rather than a false green, but the capability is unreachable until the producer records attribution.

## Steps to Reproduce

Run the census candidates subcommand against a real mutation report. It exits non-zero saying the killed mutants carry no per-test attribution and the run must be repeated with it. Search the repository for the attribution key: it appears only in the consumer and the consumer's own test.

## Proposed Fix

Have mutation.py record which test killed each mutant - run the suite per test, or parse the runner's per-test results - so the consumer has evidence to read. Until then US0507 is consumer-only and says so.

## Acceptance Criteria

### AC1: a killed mutant carries the test that killed it

- **Given** a pytest or unittest failure in the runner's output
- **When** it is read
- **Then** the node id is parsed and attached to the record, so the prune-candidate consumer has the key it requires instead of taking its refusal branch against every real report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_a_pytest_failure_is_attributed
- **Verified:** yes (2026-07-29)

### AC2: both runners are parsed

- **Given** a unittest FAIL or ERROR header
- **When** it is read
- **Then** it is attributed too, because a parser knowing one runner would attribute nothing for the other - the same silence this fix exists to end
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_a_unittest_failure_is_attributed
- **Verified:** yes (2026-07-29)

### AC3: output naming no test attributes nothing

- **Given** output the parser cannot read
- **When** it is read
- **Then** no attribution is recorded - honest, and not an error: a fabricated one would be evidence about the wrong test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_output_naming_no_test_attributes_nothing
- **Verified:** yes (2026-07-29)

### AC4: the producer emits the key

- **Given** the run loop
- **When** it is read
- **Then** it attaches the killing test on a kill, because a parser nothing calls would leave the consumer refusing exactly as before
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_the_run_loop_records_the_key_on_a_kill
- **Verified:** yes (2026-07-29)

### AC5: the runner's output is captured

- **Given** `_run_tests`
- **When** it is read
- **Then** it pipes rather than discarding to DEVNULL - the precondition, without which the attribution could only ever be absent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_the_runner_output_is_captured_not_discarded
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ closing review) | Filed |
