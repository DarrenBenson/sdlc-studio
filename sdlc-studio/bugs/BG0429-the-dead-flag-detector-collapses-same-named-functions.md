# BG0429: the dead-flag detector collapses same-named functions module-wide, so a dead flag reads clean and a live one reads dead

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; the live lane still reports 0 dead and the five collided modules now read unjudged rather than silently clean)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
> **Evidence:** Executed by an independent reviewer with probes under /tmp; both directions reproduced, and the five colliding modules enumerated.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`_functions` builds one dict keyed by BARE NAME over the whole module, so the last definition BFS reaches wins. `_callees` then resolves a forwarded value into the wrong function body and `_param_consumed` judges the wrong parameter. Two ordinary verb handlers each with a local helper of the same name is enough: the reviewer's fixture reported `0 dead flag(s), 0 not judged` for a genuinely dead flag - silently clean, not even unjudged - and, with the helper bodies swapped, reported a live flag as DEAD. A class method colliding with a module-level function also misjudges, because `self` absorbs argument index 0. Five modules already in the scanned set carry duplicate function names (artifact, critic, lib/`run_state`, sprint, validate); the reviewer confirmed by differential run that no verdict flips today, so this is latent rather than firing.

## Steps to Reproduce

1. A module with `def cmd_a(args)` and `def cmd_b(args)`, each containing a local `def emit(v)` - one body consuming its argument, the other not.
2. Forward `args.alpha` to the non-consuming `emit` and `args.beta` to the consuming one.
3. `command_audit.dead_flags(source)` reports no dead flag; swap the two bodies and it reports the live flag dead.

## Proposed Fix

Key `_functions` by SCOPE rather than by bare name, and strip `self` for any method rather than only for `__init__`.

## Acceptance Criteria

### AC1: a module with colliding function names is NOT JUDGED, with the reason

- **Given** two verb handlers each forwarding into a local helper of the same name, one of which reads a flag and one of which does not
- **When** the dead-flag detector runs
- **Then** no flag is reported dead and the destinations are reported unjudged, naming the collision - the resolver keys functions by bare name over the whole module, so the last definition the walk reaches wins and a forwarded value resolves into the WRONG body. The reviewer's fixture reported `0 dead flag(s), 0 not judged` for a genuinely dead flag, which is silently clean and worse than either honest answer, and with the helper bodies swapped it reported a LIVE flag as dead
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_module_with_COLLIDING_function_names_is_not_judged
- **Verified:** yes (2026-07-31)

### AC2: a module with no collision still reports a dead flag

- **Given** an ordinary module with one unread flag
- **When** the detector runs
- **Then** it is still reported dead - refusing to judge a collided module must not become refusing to judge, and a lane that can no longer fail is not a lane
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_module_with_NO_collision_still_reports_a_dead_flag
- **Verified:** yes (2026-07-31)

### AC3: the collision helper finds exactly the duplicates

- **Given** a module defining one name twice at module level and another shared between a module function and a class method
- **When** the helper runs
- **Then** it returns both and nothing else - asserted on its own so a change to the reporting cannot quietly empty it, which is how a guard becomes green and inert
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_collided_names_finds_exactly_the_duplicates
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
