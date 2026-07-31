# BG0457: Four spec-agreement guards pin prose to prose: a set comparison that cannot fail in the reverse direction, a whole-file substring satisfied by the Revision History row describing the change, a word-presence check an unrelated sentence already satisfies, and a source-substring wiring check a comment satisfies

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** tools/tests/test_trd_surface_derivation.py, tools/tests/test_token_premise.py, tools/tests/test_adr011_agreement.py, sdlc-studio/trd.md
> **Evidence:** Independent adversarial review of RUN-01KYTKA1 tranche B (product seat, isolated worktree, 41 mutants applied, 10 survived). US0457=REJECT, US0458=REJECT, US0459=REJECT.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Four guards over EP0168's spec-agreement work assert something weaker than the criteria they verify claim, and each survives a mutation that the criterion says must redden it. The shape is the same every time: the guard reads a document and compares it against a projection of itself, so the document can agree with the guard while disagreeing with the code.

US0458: the guard computes `named = _backticked(block) & types` and then asserts only `types - named == set()`. `named` is a subset of `types` by construction, so the doc-to-code direction is structurally unrepresentable. AC1 says the guard "fails in either direction", AC2 says a lane added to OR REMOVED FROM the registry reddens, AC3 says "both equal the shipped set" - all three are false of the shipped guard.

US0459: the guard asserts the strings "lower bound" and "supplied" appear somewhere in a lowercased whole-file read. The Revision History row describing this very change contains both, so the two passages that actually state the premise can be gutted and the guard stays green. It is pinned to prose ABOUT the claim, not the claim, which is what AC2 forbids in terms.

US0457: the ADR half is satisfied by `assertIn(word, block)` over three words, and an unrelated pre-existing sentence already carries one of them, so the whole D0062 fail-safe sentence can be deleted green. The wiring half uses `assertIn("grooming_report", inspect.getsource(...))`, a substring over source text, so replacing the real call with a comment that merely names it survives - falsifying AC3's stated mutation exactly.

## Steps to Reproduce

Each mutant applied singly, anchor asserted unique, `__pycache__` purged, `python3 -B`, reverted per file.

```text
US0458  remove `"window": _window,` from gate.py DEFAULT_CHECKS      SURVIVED (whole guard file)
US0458  remove `"spawned-column",` from reconcile.py DRIFT_KINDS      SURVIVED
US0458  insert a fictional `telepathy-lane` into the TRD gate prose   SURVIVED
US0459  gut trd.md:634-635 (the passage stating the premise)          SURVIVED
US0459  gut trd.md:1084                                              SURVIVED
US0459  gut BOTH together                                            SURVIVED
US0457  delete the entire D0062 fail-safe sentence, trd.md:998-1000   SURVIVED
US0457  replace the grooming_report call at sprint.py:4782 with a
        comment that names it                                        SURVIVED
```

The `window` mutant died only across the full 574-test tools suite - by a sibling guard, not by US0458's own.

## Proposed Fix

For the set comparison: assert equality in both directions against the shipped registry, not `types - named`. The reverse direction is the one that catches a document naming a lane the code does not have.

For the substring guards: anchor on the passage, not the file. A whole-file `assertIn` over a document that also contains a Revision History describing the change can never fail, because the change's own description satisfies it. Assert against the specific block, and assert the block's absence reddens.

For the wiring check: assert the call is REACHED, not that its name appears in the source. A comment naming a function is indistinguishable from a call to it under `inspect.getsource`.

## Acceptance Criteria

- [ ] The TRD surface guard fails in BOTH directions: removing a lane from the shipped registry and adding a fictional lane to the TRD each redden it, verified by applying both mutants
- [ ] The token-premise guard is anchored to the passages that state the premise, not to a whole-file substring the Revision History satisfies: gutting both passages reddens it
- [ ] The ADR-011 agreement guard reddens when the D0062 fail-safe sentence is deleted, rather than passing on a word an unrelated sentence already carries
- [ ] The close-side wiring check reddens when the real call is replaced by a comment naming it, so it asserts the call is reached rather than that its name appears in the source

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
