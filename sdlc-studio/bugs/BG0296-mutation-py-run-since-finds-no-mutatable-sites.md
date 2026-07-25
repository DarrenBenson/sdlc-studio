# BG0296: mutation.py run --since finds no mutatable sites for a diff that only adds guard clauses, so a change made entirely of if-condition/raise guards cannot be mutation-verified through the diff surface

> **Status:** Open
> **Created:** 2026-07-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Severity:** Medium
> **Points:** 3

## Summary

A change whose new lines are all guard clauses - if _id(x) in `some_set()`: raise, and boolean membership/comparison conditions - reports 'nothing to mutate: the selected surface has no mutatable sites (empty surface)'. The mutation surface selection does not treat those guard conditions as mutatable sites, so a defensive change built of guards has zero mutation coverage from the diff-scoped run and the discipline silently reports 0/N files covered.

## Steps to Reproduce

1. Make a change that adds guard clauses to a function (e.g. an independence check: if _id(authoriser) in `worker_ids(...)`: raise ValueError(...)). 2. Run mutation.py run --since HEAD --files <file> --test <suite>. 3. Observe: 'mutation: nothing to mutate - the selected surface has no mutatable sites' and, from the gate, 'mutation evidence covers 0/N file(s) of the changed surface'.

## Proposed Fix

Cover guard-clause sites in the mutable-site selection: the membership operator (in / not in), the boolean connectives (and/or) and the comparison operators inside an if that leads to a raise/return are exactly the guards a defensive change lives in, and negating one is a canonical mutant. At minimum, when the changed surface reduces to guard-only lines, report it as an uncovered gap loudly rather than as an empty surface indistinguishable from a no-op.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-25 | sdlc-studio | Created via `new` (deterministic) |
