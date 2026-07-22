# BG0256: A Done story read Verified yes for two days against a test that does not exist, because nothing rechecks a verifier's target after the stamp

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py,.claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found when RUN-01KY3MFX ran the full AC verifier over the workspace, which had not happened in some time. US0265 is Done and its AC5 named `pytest tests/test_critic.py -k test_neutrality_check_is_mechanical`. That test does not exist and does not exist at HEAD either, and the sprint never touched `test_critic.py` - so this is pre-existing, not a regression. The AC carried `Verified: yes (2026-07-20)` throughout. What the selector actually does is match nothing, and pytest then reports `98 deselected, 0 selected` and exits 0 on some paths, which is why it read green: the story was verified against an empty set. The vacuity gate caught it correctly the moment the verifier was re-run, flipping it to `no`, but two days passed in which a Done story was resting on a test nobody could have run. The intended target was almost certainly `test_neutral_text_reports_no_violations`, which exists, is mechanical, and passes - so the criterion was always satisfiable and only its POINTER was wrong. This is L-0162 restated (an AC's freshness must cover whether its verifier still exists) and it is the same family as the batch it was found in: a label claiming more than the thing behind it. The gap is that a stamp is only invalidated by an AC-text change, so renaming or deleting the TEST leaves a green stamp untouched until something re-runs the whole suite - and nothing routinely does.

## Steps to Reproduce

1. Check out the repository at any commit between 2026-07-20 and 2026-07-22. 2. Read US0265 AC5: it carries a Verify line naming `test_neutrality_check_is_mechanical` and a Verified stamp reading yes. 3. Search `test_critic.py` for that test name. Observed: no such test, at that commit or any other. 4. Run the AC's own verifier by hand: pytest on `test_critic.py` with that -k selector. Observed: 98 collected, 98 deselected, 0 selected. 5. Run the full verifier over the workspace. Observed: the AC flips to no, having read yes for two days.

## Proposed Fix

Make a stamp depend on the verifier RESOLVING, not only on the AC text being unchanged. The cheapest form: when conformance or the freshness check reads a green stamp, confirm the selector still selects at least one test, and treat a selector matching nothing as stale rather than green - the vacuity rule already exists for a live run, so this extends it to a recorded one. A periodic full re-run would also surface it, but only as often as somebody remembers, which is what allowed this. Re-pointing US0265 AC5 at `test_neutral_text_reports_no_violations` fixes THIS instance and is not the fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
