# BG0256: A Done story read Verified yes for two days against a test that does not exist, because nothing rechecks a verifier's target after the stamp

> **Status:** Fixed
> **Verification depth:** functional - 5 tests in StampResolutionTests plus a conformance discrimination test holding every argument but dead_stamps identical; six hand-applied mutants all killed with bytecode purged under python3 -B; the two live shapes reproduced end to end and the command exits 1 on them
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py,.claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py,.claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found when RUN-01KY3MFX ran the full AC verifier over the workspace, which had not happened in some time. US0265 is Done and its AC5 named `pytest tests/test_critic.py -k test_neutrality_check_is_mechanical`. That test does not exist and does not exist at HEAD either, and the sprint never touched `test_critic.py` - so this is pre-existing, not a regression. The AC carried `Verified: yes (2026-07-20)` throughout. What the selector actually does is match nothing, and pytest then reports `98 deselected, 0 selected` and exits 0 on some paths, which is why it read green: the story was verified against an empty set. The vacuity gate caught it correctly the moment the verifier was re-run, flipping it to `no`, but two days passed in which a Done story was resting on a test nobody could have run. The intended target was almost certainly `test_neutral_text_reports_no_violations`, which exists, is mechanical, and passes - so the criterion was always satisfiable and only its POINTER was wrong. This is L-0162 restated (an AC's freshness must cover whether its verifier still exists) and it is the same family as the batch it was found in: a label claiming more than the thing behind it. The gap is that a stamp is only invalidated by an AC-text change, so renaming or deleting the TEST leaves a green stamp untouched until something re-runs the whole suite - and nothing routinely does.

## Steps to Reproduce

1. Check out the repository at any commit between 2026-07-20 and 2026-07-22. 2. Read US0265 AC5: it carries a Verify line naming `test_neutrality_check_is_mechanical` and a Verified stamp reading yes. 3. Search `test_critic.py` for that test name. Observed: no such test, at that commit or any other. 4. Run the AC's own verifier by hand: pytest on `test_critic.py` with that -k selector. Observed: 98 collected, 98 deselected, 0 selected. 5. Run the full verifier over the workspace. Observed: the AC flips to no, having read yes for two days.

## Proposed Fix

Make a stamp depend on the verifier RESOLVING, not only on the AC text being unchanged. The cheapest form: when conformance or the freshness check reads a green stamp, confirm the selector still selects at least one test, and treat a selector matching nothing as stale rather than green - the vacuity rule already exists for a live run, so this extends it to a recorded one. A periodic full re-run would also surface it, but only as often as somebody remembers, which is what allowed this. Re-pointing US0265 AC5 at `test_neutral_text_reports_no_violations` fixes THIS instance and is not the fix.

## Acceptance Criteria

### AC1: a recorded green whose selector no longer resolves reads stale, not green

- The freshness judgement stops depending only on the AC text. A recorded pass whose
  verifier names a pytest node or `-k` pattern that selects nothing is reported STALE,
  with the AC id and the unresolvable selector named, so the reader is told which pointer
  died rather than that the story "changed".
- Both shapes are covered: a node address whose class or method no longer exists, and a
  `-k` pattern that matches nothing while the file it names still collects. The second is
  the shape that produced this bug and the one a file-exists check would pass.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::StampResolutionTests::test_a_recorded_green_whose_selector_selects_nothing_is_reported_stale

### AC2: conformance refuses to count a Done story verified on an unresolvable stamp

- The `verified` stage of `conformance.py` reads the resolution result, so a Done story
  whose AC carries `Verified: yes` against a selector that selects nothing is
  non-conformant and appears in `missing` with a reason a reader can act on.
- The existing remediation registry carries a hint for whatever finding kind this adds, so
  the guard that derives its key set from the stage vocabulary stays green.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::StampResolutionTests::test_a_done_story_stamped_against_a_selector_that_resolves_to_nothing_is_not_verified

### AC3: a resolving selector stays green, and the check collects rather than runs

- Negative control: a stamped AC whose selector still selects at least one test is left
  green and is not re-run. Without this the fix is indistinguishable from marking every
  stamp stale, which would be the same defect with the sign flipped.
- Resolution is decided by collection, not execution, so the check costs a collection pass
  per distinct selector and executes no test body - it can therefore run beside the
  freshness check rather than only in a full suite sweep, which is what let two days pass.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::StampResolutionTests::test_a_resolving_selector_stays_green_and_no_test_body_is_executed

### AC4: the condition is catchable from the command line, on a story, without a suite run

- `verify_ac` exposes the check over a named story and exits non-zero when a stamped
  verifier cannot resolve, printing the story, the AC and the selector. The condition then
  has a routine that finds it, which is the gap this bug records.
- The instance that produced this bug is repaired in the same change: US0265 AC5 is
  re-pointed at `test_neutral_text_reports_no_violations`, which exists and passes. That
  repair is stated as a completion item, not as the fix.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::StampResolutionTests::test_the_command_exits_non_zero_on_a_story_whose_stamped_verifier_cannot_resolve

## Resolution

`selector_resolves` asks the runner what a selector would SELECT, by collection rather than
execution: `pytest --collect-only`. Exit 5 (collected nothing) and exit 4 (usage error, e.g. a
node whose class is gone) both mean the pointer is dead; exit 0 means it is live. The check
costs an import and runs no test body, so it sits beside the freshness check instead of only
inside a full suite sweep - which is what let two days pass.

`unresolvable_stamps` reports only ACs recorded green: an unstamped AC claims nothing, so a
dead selector there is the author's business at the next run, not a false green on disk.

`conformance` no longer counts a Done story verified while any stamp rests on a dead pointer,
and `verify_ac stamps` exposes the check per story with a non-zero exit, naming the story, the
AC and the selector - the routine the condition lacked. `--bugs` reaches
`sdlc-studio/bugs`, which `walk_stories` does not.

**Unanswerable is kept distinct from unresolvable.** A `manual`, `grep` or `shell` selector
returns None rather than False; calling it dead would mark every non-pytest stamp stale.

US0265 AC5, the instance that produced this bug, was already re-pointed at
`test_neutral_text_reports_no_violations` when the bug was filed, and it resolves.

Mutation: six applied, six killed - exit 5 treated as resolving, `--collect-only` dropped so
the check would EXECUTE, unanswerable reported as dead, unstamped ACs checked too, the command
always exiting 0, and conformance ignoring dead stamps. The third survived at first and was
NOT equivalent: it returned None for every tested input only by luck downstream, so the guard
could have been deleted with the suite green while the check began shelling out for verifiers
it cannot answer. The test now pins that no subprocess is spawned at all.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
| 2026-07-22 | sdlc-studio | Fixed, then the fix's OWN regression fixed in the same wave: baking a per-AC `pytest --collect-only` into conformance turned an 8s gate into 81s across 306 stamped stories. The collection is now cached per test FILE and every selector - node address, class prefix, `-k` boolean - resolves in-process against the cached node list, so the workspace costs one collection per distinct file. Gate back to 15s, same verdicts. Caught by the gate-budget guard reporting +366pc, not by a test. |
