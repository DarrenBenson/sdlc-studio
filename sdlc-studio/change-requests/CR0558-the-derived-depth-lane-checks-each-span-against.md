# CR-0558: the derived-depth lane checks each span against its own seal rather than re-deriving it, so a unit whose ledger evidence was evicted still passes

> **Status:** Proposed
> **Priority:** High
> **Type:** enhancement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Adversarial review of BG0606, 2026-08-25. US0671 and US0676 both report EVIDENCE ABSENT from `verify_ac.py depth` while the `derived-depth` lane passes them; eviction traced to a `register_mutant` call at 14:03:35 against an edited `verify_ac.py`, predating the run's base ref.
> **Date:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`gate.py`'s `derived-depth` lane validates each `[[derived: ... | fp <hash> ]]` span against the fingerprint stamped beside it, and reports 'every derived half matches its own seal'. A seal only proves the span has not been hand-edited since it was written; it says nothing about whether the evidence behind it still exists. Measured 2026-08-25: US0671 is stamped `fp 1fb328bab2e6` and the instrument now derives `fp f459a68642cb`, because a later `register_mutant` call against an edited `verify_ac.py` evicted all 14 of its rows - registration is keyed on the target's content hash, so any edit to a shared file empties every unit registered against it earlier. `verify_ac.py depth --unit US0671` reports EVIDENCE ABSENT. The lane passed 1303 units while at least two of them carried a derived half no longer true. BG0550 made the eviction LOUD at the moment it happens; nothing makes it visible afterwards, and this lane is where it would be seen.

## Impact

A `Verification depth` field is the artefact's claim about how hard its evidence was tested, and the close, the release notes and every reviewer read it. A lane that certifies those fields while unable to see an emptied ledger converts a stale claim into a passed check, which is worse than not checking - a reviewer who sees the lane green stops looking.

## Acceptance Criteria

- [ ] Given a unit whose stamped derived half no longer matches a fresh derivation, when the `derived-depth` lane runs, then that unit is REPORTED by name with both fingerprints - a seal proves only that the span was not hand-edited, and says nothing about whether the evidence behind it still exists
- [ ] Given a unit whose stamped span matches a fresh derivation, when the lane runs, then it is silent about that unit - the paired control, so the lane does not become a warning that always fires and is therefore never read
- [ ] Given a corpus in which some unit's ledger rows were evicted by a later registration against the same target file, when the lane runs, then the eviction is visible from the lane's output alone, without anyone thinking to ask `verify_ac.py depth` about that particular unit

## Recommendation

1, ratcheted. Re-derive, report as advisory while the yield is measured, and block once the corpus is clean - the same shape `claim-drift` and `revert-check` ship under. A seal that certifies its own freshness is the class of check this project has repeatedly found worthless, and this one certifies 1303 units.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Raised |
