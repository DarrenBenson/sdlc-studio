# BG-0014: Story Verify lines do not test what their ACs assert: broken shell expressions, regex-metachar failures, and source-grep smoke tests

> **Status:** Open
> **Severity:** High
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

Across all five stories the executable Verify DSL fails its own purpose - US0005 AC2 actually FAILS the verifier on correct code (regex metachar), US0001/US0004 absence-ACs pass vacuously regardless of regression, US0005's exit-code AC is a dead-branch tautology, and many behavioural ACs (US0001 AC4, US0002 AC2/AC4/AC5, US0003 AC1/AC3/AC4/AC5) are backed by source/doc greps that match a literal string rather than the behaviour.

## Problem

Verified empirically and by inspection: (1) US0005 AC2 'grep "next_num = base + 1"' fails through verify_ac.py because grep routes to rg/grep -E (regex): '+' means one-or-more, no match - a Ready story is blocked by its own gate on correct code (next_id.py:77). (2) US0004 AC5 'grep -qv -- "--full"' passes whenever any help line lacks --full, so a future --full flag is undetectable (passes here only on this box's ugrep). (3) US0001 AC5 'test "$(...; echo $?)" = 0 -o "$?" = 1' has a dead second branch ($? reads the prior shell command, not detect), so the exit-1-on-drift contract is never tested. (4) Behavioural ACs backed by 'grep <token> <source/doc>' (US0001 AC4 grep read-only reconcile.py; US0002 AC2 grep Verified:, AC4 grep generated_at, AC5 grep require_ac_verification in a reference doc; US0003 AC1 key-presence only, AC3 grep persona_usage - passes despite the known-broken persona output, AC4 grep ac_verification, AC5 grep prep) stay green through behavioural regressions as long as the literal string survives.

## Proposed Fix

Make absence-ACs portable and real (US0004 AC5: 'shell ! python3 .../status.py pillars -h | grep -q -- "--full"'; US0003 AC5: snapshot-and-diff .local/). Fix US0005 AC2 to be regex-safe (escape '+' or match a metachar-free fragment) or add a grep -F fixed-string mode to the DSL. Fix US0001 AC5 by capturing the code into a variable reused on both operands, or split into clean/seeded-drift fixtures. Replace source/doc-grep behavioural verifiers (US0001 AC4, US0002 AC2/AC4/AC5, US0003 AC1/AC3/AC4) with assertions that exercise behaviour against a tmp fixture, routing to a pytest node where a one-liner cannot fixture-build.

## Evidence

Empirical: 'verify_ac.py run --story US0005-next-id-allocation.md --dry-run' -> 'ac=5 pass=4 fail=1 ... FAIL AC2'; the DSL builds 'rg -q <pattern>' / 'grep -rqE <pattern>' at verify_ac.py:201-203 (regex mode) vs literal Verify line US0005-next-id-allocation.md:65 'grep "next_num = base + 1"'

## Impact

The Verify-line DSL exists so 'Done' means 'AC passed against live code' (US0002 background: ticked ACs regressed within a week). These verifiers re-introduce exactly that gap: behavioural regressions stay green, absence-ACs cannot fail, and the only Ready story whose AC actually runs (US0005) reports a spurious failure - eroding trust in the gate in both directions.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: stories-ac) |
