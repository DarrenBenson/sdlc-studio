# BG0300: `manual` is a gate-bypass token: a story whose ACs are all manual reaches Done with the verify gate checking nothing

> **Status:** Open
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Provenance:** Raised downstream as homelab BG0144 from an independent Product review of US0151; confirmed in this repo's source
> **Raised-by:** Claude Code; human; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Severity:** High
> **Points:** 3

## Summary

`_done_verify_gate` returns None - "nothing executable to verify" - whenever `_story_has_executable_acs` is False, and that helper is False when every `Verify:` line is `manual`:

```text
transition.py:106 def _story_has_executable_acs(text) -> bool:
transition.py:122 if not _story_has_executable_acs(text):
transition.py:123 return None # nothing executable to verify
```

So `manual` does not mean "a human checks this". It means "nothing checks this". A story can go Draft -> Done in a single transition with the deterministic gate having looked at no part of the deliverable.

The incentive runs the wrong way. The more physical and irreversible the work - a live VIP failover, a disk swap, a database cutover - the more its acceptance criteria MUST be `manual`, and so the less the tool checks before letting it reach Done. The riskiest work in any project is the least gated, by construction.

A worked example from the downstream project: a keepalived VIP-failover rehearsal story with five ACs, all correctly `manual`, transitioned Draft -> Done in one commit whose own message read "Left In Progress, not Done". Three gates were green and not one looked at the deliverable - the verify gate returned None (this bug), the manual-AC linter passed because it checks an AC NAMES an observable outcome rather than that anyone OBSERVED one, and conformance exempted the unit via the very threshold that unit had caused to be raised.

Note what is NOT being asked for here. Nobody wants the tool to pretend it can watch a VIP move.

## Steps to Reproduce

1. Author a story whose every AC carries `- **Verify:** manual <observable outcome>`.
2. `transition.py` it Draft -> Done.
3. It succeeds. `_done_verify_gate` returned None at transition.py:123 without evaluating anything, and no evidence that a human looked is required or recorded anywhere.
4. Confirm the helper is the cause: transition.py:111 treats any first token of `manual`/`manually` as non-executable, and a story with only those has `_story_has_executable_acs` False.

## Proposed Fix

Do not make the gate evaluate manual ACs - it cannot. Make it require EVIDENCE that a human did.

When a story reaching Done has manual ACs, require each to carry a `**Verified:**` marker naming when it was observed and by whom, and fail the transition when one is bare. That closes the bypass without pretending a machine can watch a VIP move, and it is consistent with the doctrine's existing prohibition on hand-stamping an AC a machine did not check - today nothing forbids NOT stamping at all, which is strictly worse, being the same absence of evidence with no admission of it.

Returning None should also be distinguishable from passing at the call site: `None` currently reads as "no opinion" and is consumed as "no objection". A third state - `UNCHECKED` - that the caller must handle explicitly would have made this visible when it was written.

A reference implementation of the evidence check (plus the companion `Affects`-paths-exist check, and 27 tests over real corpus shapes) is in the downstream homelab repo at `utilities/sdlc/check_done_stories.py`, written against BG0144. It runs over a 141-Done-story corpus and finds 11 failures, so the rule is enforceable in practice, not just in principle.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | Claude Code | Created via `new` (deterministic) |
