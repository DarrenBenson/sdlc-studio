# BG0145: telemetry CLI rejects the new rate seed-source, and complexity drops derivable churn risk for a docs unit

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Effort:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/complexity.py
> **Points:** 3
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

## Acceptance Criteria

### AC1: churn-based risk survives for a docs unit even when code complexity is inapplicable

- **Given** a constantly-churning markdown file (no scored functions, so code difficulty is `unknown`)
- **When** `complexity.assess` scores the change
- **Then** `applicable` is False and `difficulty` is `unknown` (code signal absent) BUT `risk_band` reflects the churn (`high` for a hot doc); a quiet doc stays `low`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_complexity.py::CompositeRiskTests::test_assess_carries_churn_risk_for_a_docs_file

### AC2: part (1) - the seed-source CLI restriction - is obsolete (resolved by RFC0038)

- **Given** RFC0038 (CR0265-CR0267) replaced the per-unit forecast (and its `seed`/`seed_source`/`complexity` inputs) with the points model
- **When** telemetry.py is inspected
- **Then** there is no `--seed-source` CLI argument, so the complexity|effort|none restriction the bug describes no longer exists - nothing to fix
- **Verify:** manual - `grep -c 'seed-source' .claude/skills/sdlc-studio/scripts/telemetry.py` returns 0

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
| 2026-07-15 | sdlc-studio | Fixed part (2): assess keeps churn risk for a docs unit; part (1) declined - the seed-source CLI it names was removed by RFC0038 |
