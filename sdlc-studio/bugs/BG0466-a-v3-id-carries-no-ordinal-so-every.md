# BG0466: A v3 id carries no ordinal, so every v3 artefact scores 0 against the provenance cutoff and is exempted as pre-adoption legacy; and the run-scoping discriminator on the finding-placement count is unguarded

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/provenance.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Rejoinder review of the BG0465 repair (engineering seat, isolated worktree, base 6f91b24b). Both established by driving the production entry points directly rather than by reading.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Two findings the rejoinder raised that are NOT the repair it was reviewing, and are carried rather than folded into it.

The provenance check exempts an artefact whose id number falls at or below the adoption cutoff. `id_number` returns None for a v3 ULID by design - a ULID carries no ordinal - so every v3 artefact scores 0, falls under any cutoff, and is exempted as pre-adoption legacy. An ordinal cutoff cannot rank an id that carries no ordinal. The check therefore reports clean over the whole family of ids the product now mints by default, and it does so silently: an exemption and a pass render identically.

Separately, `sprint.py`'s out-of-batch finding count is what makes the close's placement line mean "this run" rather than "this repo, ever". Its run-scoping predicate is unguarded: replacing the whole condition with `True` survives all 624 tests of the module, while genuinely changing behaviour - a pre-existing unstamped backlog bug then counts as this run's close work. The number the sprint goal points at can drift into a repo-lifetime tally with the suite green.

## Steps to Reproduce

```text
provenance, probed through check():
  an UNSTAMPED v3 bug `BG-01JQK3F8AA`  -> no finding, before and after the BG0465 sweep
  id_number('BG-01JQK3F8AA')            -> None  -> idn 0 -> under any cutoff -> exempt
  id_number('BG-9007')                  -> 9007  (the hyphenated v2 case, now correct)

sprint.py, the run-scoping predicate:
  `if `raised_in.startswith(`"none open") and started:`  ->  `if True:`
  SURVIVED all 624 tests of test_sprint.py
  probe: one pre-existing unstamped backlog bug
         -> 1 under the mutant, 0 on clean
```

## Proposed Fix

For provenance: rank by something a v3 id has. An adoption cutoff expressed as an ordinal is the wrong instrument for a ULID - either resolve the cutoff to a DATE and compare the artefact's own recorded date, or treat an id with no ordinal as NOT exempt and let the stamp check speak. What must not stand is a whole id family exempted by an accident of parsing, reported identically to a pass.

For the placement count: pin the discriminator. A test that varies only the stamp - a finding raised inside the run's window against one predating it - separates "this run" from "this repo, ever", which is the distinction the line's own sentence claims to be making.

## Acceptance Criteria

- [ ] An unstamped v3 artefact is either checked or REPORTED as exempt with the reason, rather than silently passing the provenance check because its id carries no ordinal to compare against the cutoff
- [ ] The provenance cutoff's treatment of an id with no ordinal is asserted by a test, so the answer is a decision on the record rather than a consequence of `id_number` returning None
- [ ] Replacing the run-scoping predicate on the out-of-batch finding count with a constant reddens the suite, so the placement line cannot drift from `this run` to `this repo, ever` with the tests green

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
