# BG0457: Four spec-agreement guards pin prose to prose: a set comparison that cannot fail in the reverse direction, a whole-file substring satisfied by the Revision History row describing the change, a word-presence check an unrelated sentence already satisfies, and a source-substring wiring check a comment satisfies

> **Status:** Open
> **Verification depth:** functional (nine mutants applied singly against the shipped guards - the two registries, the router table, both directions of the TRD enumeration, both stating passages, the fail-safe sentence and the close-side call - anchors asserted unique, `__pycache__` purged, each child run under `python3 -B`, sources restored byte-identical)
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

- [x] **AC1: the surface comparison is an equality, so it reddens in both directions and outside the enumeration.**
  - **Given** a passage that enumerates names and a shipped registry to hold it to
  - **When** the comparison runs
  - **Then** it refuses a name the registry does not carry, a registry name the passage omits, and a name smuggled into the passage's prose outside the enumeration. **The mutants:** adding `telepathy-lane` to the TRD's gate-tier list, and adding it to the sentences around the list, must each redden - under the shipped `named = _backticked(block) & types` both were unrepresentable, because the intersection made the compared set a subset of the registry by construction
  - **Verify:** pytest tools/tests/test_trd_surface_derivation.py::TheSurfaceComparisonFailsInBothDirections::test_the_comparison_fails_in_both_directions_and_outside_the_enumeration
  - **Verified:** yes (2026-08-11)

- [x] **AC2: the lower-bound claim is read from the passages that state it, not from the file that describes it.**
  - **Given** a document whose stating passage has been emptied and whose Revision History still carries the row describing this change - the exact state three surviving mutants left `trd.md` in
  - **When** the guard reads it
  - **Then** it refuses, and accepts the same document with the passage restored. **The mutant:** gutting either stating passage must redden. Under the shipped whole-file `assertIn("lower bound")` plus `assertIn("supplied")` both passages could be gutted together and the row describing the change satisfied both strings
  - **Verify:** pytest tools/tests/test_token_premise.py::TheLowerBoundClaimIsAnchoredToItsPassage::test_a_revision_history_row_does_not_stand_in_for_the_stating_passage
  - **Verified:** yes (2026-08-11)

- [x] **AC3: the ADR's fail-safe rule is pinned to the sentence that states it.**
  - **Given** the ADR-011 Decision with the D0062 fail-safe sentence deleted, the unrelated "an absent config BLOCKS and an unknown mode falls back to enforce" left standing
  - **When** the guard reads it
  - **Then** it refuses, because no single sentence says an absent, an empty and an off-ladder goal all block, and it still refuses when those words are scattered across two sentences. **The mutant:** deleting the whole D0062 fail-safe sentence from `trd.md` must redden; under `assertIn(word, block)` over three words the config sentence already carried two of them
  - **Verify:** pytest tools/tests/test_adr011_agreement.py::TheAgreementChecksDiscriminate::test_deleting_the_fail_safe_sentence_is_refused
  - **Verified:** yes (2026-08-11)

- [x] **AC4: the close-side counterweight is observed as a reached call.**
  - **Given** the close's review-anchor step run over a throwaway root on the `design` rung, with `sprint.grooming_report` spied at the module global the call resolves through
  - **When** the step completes
  - **Then** the spy recorded a call carrying the fixture batch, and the same step on the `done` rung recorded none. **The mutant:** replacing the call with a comment that names it must redden; under `assertIn("grooming_report", inspect.getsource(...))` a comment and a call are the same string
  - **Verify:** pytest tools/tests/test_adr011_agreement.py::TheAgreementChecksDiscriminate::test_the_close_calls_the_grooming_report_only_on_the_design_rung
  - **Verified:** yes (2026-08-11)

## Verification evidence

Functional. Nine mutants applied singly, each anchor asserted to occur exactly once, `__pycache__`
purged and each child run under `python3 -B`, the patch asserted to have changed the file on disk,
and every source restored byte-identical afterwards.

| Mutant | Suite | Result |
| --- | --- | --- |
| remove `window` from `gate.DEFAULT_CHECKS` | surface | killed |
| remove `spawned-column` from `reconcile.DRIFT_KINDS` | surface | killed |
| add a fictional lane INSIDE the TRD gate-tier enumeration | surface | killed |
| add a fictional lane to the TRD gate-tier prose, outside the enumeration | surface | killed |
| rename a row in the router's Type Reference table | surface | killed |
| gut the section 10 passage stating the lower bound | token premise | killed |
| gut the Won't Have passage stating the lower bound | token premise | killed |
| delete the D0062 fail-safe sentence | ADR-011 | killed |
| replace the close's `grooming_report` call with a comment naming it | ADR-011 | killed |

The first four are the ones worth naming. Three of them SURVIVED the shipped guard, and the
fourth - a lane the document invents - could not have failed it at all: `named = _backticked(
block) & types` makes the compared set a subset of the registry, so `types - named == set()` has
no reverse direction to test. The repair is an equality against the passage's own enumeration,
addressed as the list rather than as loose backticked words, plus a refusal of any other name in
the passage outside a small declared prose set. That prose set is the one place this could be
switched off again, so it is per-passage, measured against the shipped text rather than guessed,
and named in the failure message.

No document changed. All four passages already agreed with the code; what did not agree was the
guards' claim about themselves.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
| 2026-08-11 | Claude Opus 5 | Groomed: each criterion names the production change that must redden it. Fixed: all four guards repaired, nine mutants killed |
