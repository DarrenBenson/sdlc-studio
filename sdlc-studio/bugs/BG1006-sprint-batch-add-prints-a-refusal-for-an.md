# BG1006: sprint batch add prints a refusal for an unresolvable Affects path but adds the unit anyway

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_add_affects_wording.py, changelog.d/BG1006.md
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T07:15:37Z

## Summary

Found in homelab RUN-01M4EMNN (2026-10-09). `sprint.py batch add BG0272 --reason ...` printed 'BG0272: Affects declares path(s) not on disk - ...' (read as a refusal) and exited, yet the unit WAS added: after the Affects line was corrected, the retry said 'added BG0272 to the batch (already present); batch is now 19 unit(s)' - the batch had grown from 17 to 19 across two 'refused' adds. A gate that reports a refusal while mutating the run is worse than no gate: the operator believes the batch is unchanged.

## Steps to Reproduce

In an open run, file a unit whose Affects names a non-path (e.g. 'HA scripts foo / bar'); run sprint.py batch add <id> --reason x - note the 'Affects declares path(s) not on disk' line; inspect .local/run-state.json batch - the unit is in it.

## Proposed Fix

Run the Affects check before the mutation and exit non-zero without writing; or, if it is advisory, say so ('warning: ... - added anyway') and print the added line. Either way the message and the state must agree.

## Acceptance Criteria

- [ ] **AC1** In `warn` mode, `sprint batch add` labels an Affects finding as a warning on a line that says the unit was added anyway, so no line of its output reads as a refusal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_add_affects_wording.py::BatchAddWordingTests::test_a_warned_add_says_it_added_the_unit
- [ ] **AC2** An Affects entry that is not a path at all (words and spaces, no file shape) is named as not a path, and never told that "a file the unit CREATES is fine"
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_add_affects_wording.py::BatchAddWordingTests::test_a_non_path_affects_is_named_as_not_a_path

## Triage

- Reproduced at 750cbd81 in the default `warn` mode: `sprint batch add BG0001` for a bug whose Affects is `HA scripts foo / bar` prints `added BG0001 to the batch; batch is now 2 unit(s)...` and then `BG0001: Affects declares path(s) not on disk - HA scripts foo / bar (a file the unit CREATES is fine)`, exits 0 and adds the unit. The state and the first line agree; the second line carries no warning label and reads as a refusal to anyone reading the last line, which is what happened in the homelab run. In `block` mode the add is refused before the write (BG0521, since August).
- Severity lowered to Low: the output is misleading, not the state. Affects corrected; criteria rewritten for what is actually wrong, including the non-path entry told a created file is fine.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
| 2026-10-09 | Claude Opus 5.5 (triage) | Triaged: reproduced on current code; Affects made repository paths; criteria made executable; severity Low |
