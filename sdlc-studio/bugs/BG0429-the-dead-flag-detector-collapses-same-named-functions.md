# BG0429: the dead-flag detector collapses same-named functions module-wide, so a dead flag reads clean and a live one reads dead

> **Status:** Open
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

- [ ] The behaviour described is corrected: `_functions` builds one dict keyed by BARE NAME over the whole module, so the last definition BFS reaches wins.
- [ ] The proposed fix lands, pinned by a test: Key `_functions` by SCOPE rather than by bare name, and strip `self` for any method rather than only for `__init__`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
