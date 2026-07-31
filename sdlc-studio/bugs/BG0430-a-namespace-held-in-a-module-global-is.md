# BG0430: a namespace held in a module global is invisible to the dead-flag detector, so a live flag is reported dead with no cannot-judge reason

> **Status:** Fixed
> **Verification depth:** functional (3/3 mutants killed; two test fixtures rewritten after they failed to discriminate)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
> **Evidence:** Executed by an independent reviewer.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`_track_namespaces` registers the target of `X = parse_args()` against the ENCLOSING FUNCTION's scope, and `global ARGS` is not modelled. A read from a sibling function walks the scope chain out to Module, finds nothing and returns False - so the read is invisible, no escape is recorded, and the destination falls straight through to `dead`. The module-global namespace is a mainstream Python idiom and it is not among the bounds the detector's docstring declares. The failure is a false positive on a blocking lane with no warning attached.

## Steps to Reproduce

1. `ARGS = None` at module level; `main()` does `global ARGS; ARGS = ap.parse_args()`.
2. A sibling `work()` reads `if ARGS.verbose:`.
3. `--verbose` is reported DEAD with an empty unjudged list.

## Proposed Fix

Model `global` (and `nonlocal`) in `_track_namespaces`, or - if that is judged out of scope - detect the shape and record it as a cannot-judge reason rather than reporting dead.

## Acceptance Criteria

### AC1: a namespace held in a module global is not invisible

- **Given** a module where `main` declares `global ARGS` and assigns `ARGS = p.parse_args()`, and a sibling function reads `ARGS.depth`
- **When** the dead-flag detector runs
- **Then** `--depth` is not reported dead - the target was registered against the ENCLOSING FUNCTION's scope and `global` was not modelled, so a sibling's read walked out to Module, found nothing, and the destination fell through to `dead`: a false positive on a blocking lane over a mainstream Python idiom the detector's own docstring did not list among its bounds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_namespace_held_in_a_MODULE_GLOBAL_is_not_invisible
- **Verified:** yes (2026-07-31)

### AC2: the declaring function can still read its own global namespace

- **Given** the same module, where `main` both declares the global and reads `ARGS.depth` itself
- **When** the detector runs
- **Then** the read is still seen - `_is_namespace` stops the chain at the first scope that BINDS the name and the declaring function does bind it, so registering the global on the module ALONE would have fixed the sibling reads and broken the declaring function's own
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_the_declaring_function_can_still_read_its_own_global_namespace
- **Verified:** yes (2026-07-31)

### AC3: a genuinely dead flag is STILL reported through a global

- **Given** a module-global namespace where one flag is read and another is not
- **When** the detector runs
- **Then** the unread one is still dead - widening what counts as a namespace must not make every flag live, and a lane that can no longer fail is not a lane
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_genuinely_dead_flag_is_STILL_reported_through_a_global
- **Verified:** yes (2026-07-31)

### AC4: a global declared in a NESTED function does not leak outward

- **Given** an outer function whose `args` is genuinely local, a nested function declaring `global args`, and an unrelated sibling reading `args.unused`
- **When** the detector runs
- **Then** `--unused` is still dead - a `global` inside a nested function binds for that function, and treating it as the outer one's declaration would register a namespace the outer scope never had, making an unrelated read count as consuming the flag. That is the false-NEGATIVE direction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_global_declared_in_a_NESTED_function_does_not_leak_outward
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
