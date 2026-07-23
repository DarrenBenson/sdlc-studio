# BG0260: Round 10's three findings, carried forward with a written repair plan instead of another unplanned fix

> **Status:** Fixed
> **Verification depth:** functional - node-addressed tests green, mutation-proven by the delivering worktree agent; merged and re-verified on the composed tree
> **Depends on:** US0315
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py,.claude/skills/sdlc-studio/scripts/mutation.py,.claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Round 10 of RUN-01KY3MFX rejected with three MAJORs, all prose, all verified by the author before filing. This bug carries them forward rather than repairing them immediately, which is CR0404's policy and CR0402's discipline applied to the round that argued for both. F1: a docstring says item 8 'was the only enumerated escape with no fixture'. Items 1, 2 and 3 have none either, verified by enumerating the fixture lists. The author reported this fixed in round 9; the edit's match string did not match, nothing changed, and the claim of a fix was made without checking - which is a worse instance of the class than the defect itself. F2: the round-9 rewrite of the over-fire paragraph DELETED the block's closing disclaimer ('Treat a green result as no contradiction in the shapes enumerated here, never as the documentation is consistent'), which was the strongest honesty statement in the file, while item 6 still says 'the closing disclaimer below does NOT cover it'. There is no disclaimer below. A repair whose purpose was to improve disclosure silently reduced it, and item 6 now makes a false structural claim about its own file. F3: mutation.py:491's comment lists `*.` among patterns matching every path. `fnmatch` matches `*.` against none of the six probes, and the CLI correctly prints '1 path(s)' for it. The comment criticising the previous version for enumerating spellings contains a wrong spelling in its own enumeration. A sibling occurrence was corrected in round 8; this one was missed because the fix was applied by string replacement without enumerating the occurrences. Also carried: a surviving mutant. Shrinking `everything_reason`'s probe battery from six paths to one passes all 3,940 tests, so five of the six probes are redundant and a shrunk battery would announce WHOLE TREE for `a*` while the matcher refuses only paths under `a`. Adding `a*` to the agreement test's claim list kills it.

## Steps to Reproduce

F1: grep the test module for 'only enumerated escape'; it is present at line 491 and the phrase 'items 1, 2 and 3' appears nowhere in the repository. Enumerate the fixture lists in DisclosedLimitsAreRealTests: items 4, 5, 6, 7 and 8 have one each, items 1, 2 and 3 have none. F2: grep the module for 'polarity scan over named topics, not a semantic proof'; it returns zero matches, while 'the closing disclaimer below' is still present in item 6. F3: run fnmatch against the six probe paths with the pattern consisting of an asterisk followed by a full stop; every result is False.

## Proposed Fix

THE PLAN, to be attacked before it is executed, per CR0402. F1: replace the sentence with one that names which items lack fixtures, and derive that list in the test rather than asserting it in prose, so it cannot rot - a test that enumerates the fixtures and asserts which items are covered would have caught both this and its previous version. F2: restore the deleted disclaimer verbatim and add a test that item 6's cross-reference resolves, since a structural claim about a file's own layout is mechanically checkable and was wrong for two rounds. F3: remove the wrong spelling, and derive the comment's examples from the probe battery rather than listing them by hand - the same derive-do-not-enumerate rule CR0394 already states, which this comment breaks while advocating it. Battery: add `a*` to the agreement test's claim list. WHAT THIS PLAN MIGHT BREAK, stated because CR0402 requires it: restoring the disclaimer re-adds lines to a file already near its budget, and deriving the comment's examples means a comment that changes when the battery changes, which is the intent but will surprise a reader expecting prose to be stable.

## Acceptance Criteria

**What makes the fix complete.** None of F1, F2 or F3 is repaired by writing a better
sentence, because a better sentence is what the previous nine rounds produced. Each
becomes a value the code computes, and the surviving mutant dies to a claim that separates
the batteries. All four states below were re-confirmed at grooming, not carried on trust.

Cost, named because CR0402 requires the plan state what it might break: restoring the
disclaimer re-adds lines to a module already near its budget, and a derived comment
changes when the battery changes, which will surprise a reader expecting prose to hold
still.

Each criterion carries its own verifier: `verify_ac` executes only the first `Verify` line
in an AC block.

### AC1: which bound items have fixtures is counted, not asserted in a docstring

- **Given** the docstring at `test_docs_single_writer.py`:491, which says item 8 "was the
  only enumerated escape with no fixture" while items 1, 2 and 3 have none either -
  re-confirmed at grooming by enumerating the fixture lists
- **When** the coverage claim is made
- **Then** it is derived by enumerating the fixture lists in `DisclosedLimitsAreRealTests`
  and comparing against the items THE BOUND names, so it cannot be wrong in prose while
  the fixtures say otherwise
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::DisclosedLimitsAreRealTests::test_which_bound_items_have_fixtures_is_derived_not_asserted

### AC2: a cross-reference to this file's own layout resolves

- **Given** item 6's "the closing disclaimer below", which occurs once in the module while
  the disclaimer it points at occurs zero times - the round-9 repair deleted it -
  re-confirmed at grooming
- **When** the module is checked
- **Then** the disclaimer is restored verbatim and every cross-reference in THE BOUND
  resolves to a block that exists, so a structural claim about a file's own layout is
  checked mechanically rather than read past for two rounds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::DisclosedLimitsAreRealTests::test_every_cross_reference_in_the_bound_resolves_within_this_module

### AC3: the comment's glob examples come from the probe battery

- **Given** `mutation.py`:491, which lists `*.` among patterns matching every path while
  `fnmatch` matches it against none of the six probes - re-confirmed at grooming
- **When** the comment names examples
- **Then** they are produced from the battery rather than typed, so an example that does
  not match every probe cannot be written - the comment criticising an enumeration of
  spellings currently contains a wrong spelling in its own enumeration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::EverythingReasonProbeTests::test_the_glob_examples_are_derived_from_the_probe_battery

### AC4: a prefix glob is not announced as the whole tree

- **Given** `a*`, which matches two of the six probes and none of the rest, and a battery
  shrunk from six probes to one, which passes the suite today
- **When** the claim list is driven
- **Then** `a*` is not announced as the whole tree, so the shrunk battery goes red and the
  five probes stop being redundant - a one-probe battery announces WHOLE TREE for `a*`
  while the matcher refuses only paths under `a`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::EverythingReasonProbeTests::test_a_prefix_glob_is_not_announced_as_the_whole_tree

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
