# BG0145: telemetry CLI rejects the new rate seed-source, and complexity drops derivable churn risk for a docs unit

> **Status:** Open
> **Severity:** Low
> **Effort:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/complexity.py
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Two small gaps left by CR0262, both reported by the agent as out of its file lane.

(1) CR0262 replaced the per-unit forecast with a flat measured rate, and sprint.py records the seed-source as `rate`. But telemetry.py CLI restricts --seed-source to complexity|effort|none, so a forecast recorded BY HAND cannot name the estimator that actually produced it. The library path sprint.py uses accepts it fine, so this only bites a human or a migration doing it manually - which is exactly what was needed to backfill the last two sprints. A vocabulary that the writer accepts and the CLI refuses is the LL0016 class: two paths to the same record disagreeing about what is valid.

(2) complexity.assess() iterates only SCORED FUNCTIONS, so for a docs unit it drops the churn-based risk signal along with the (correctly inapplicable) code complexity. But churn IS derivable for a markdown file - how often it changes is a property of the file, not of its functions. CR0262 correctly made code and risk go MISSING together for a non-code unit, which is right for code and unnecessarily lossy for risk. A docs unit that churns constantly is a different proposition from one that never changes, and the router currently cannot see the difference.

## Steps to Reproduce

1. python3 scripts/telemetry.py forecast --id X --tokens 120000 --seed-source rate -> argparse rejects it (choices: complexity, effort, none), though sprint.py writes exactly that value through the library. 2. python3 scripts/route.py estimate --unit <a docs CR> --format json -> `missing` contains both `code` and `risk`, though the churn half of risk is computable from the files git history regardless of whether it contains functions.

## Proposed Fix

(1) Add `rate` to the --seed-source choices, and derive that vocabulary from ONE place that both the CLI and the library read, so they cannot drift again. (2) Compute churn risk from the file history for any file, and reserve the MISSING marker for the code-complexity half alone - so a non-code unit still carries the signal that IS applicable to it, rather than losing both because one does not apply.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
