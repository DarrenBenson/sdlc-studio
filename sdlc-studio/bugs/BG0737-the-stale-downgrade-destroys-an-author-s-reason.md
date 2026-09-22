# BG0737: the stale downgrade destroys an author's reason on a positive verdict, so the principle BG0733 shipped is violated on the sibling branch of the same function

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Found by the independent engineering seat at BG0733 round 3, 2026-09-22, and reported rather than held as blocking because exposure today is zero. Proved at both refs with BG0499 AC1's actual line under a red selector: at HEAD the line is untouched because the old pattern could not parse it; at the delivered ref it is replaced by the marked downgrade and the author's note is lost. The reviewer resolved all 15 annotated corpus lines and found every selector either manual or unresolvable, so none is downgraded on the next run - the trap is latent, not a live loss.
> **Created:** 2026-09-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0733 established that a derived verdict never overwrites a recorded one, and enforced it on the green path. The red path does the opposite. When a criterion stamped `yes (2026-08-03) - four tests, each driving a shipped main([...])` goes red, the downgrade replaces the whole line with the marked `no`, and the author's annotation is gone from the file and recorded nowhere - `recorded_reasons` is populated only on the green path. Widening `VERIFIED_RE` is what exposed it: before BG0733 an annotated line could not be parsed at all, so the downgrade machinery could not reach it. The fix therefore gave the stale-downgrade path reach over 15 corpus lines it previously could not touch, and that path discards what it finds.

## Steps to Reproduce

1. Stamp a criterion `- **Verified:** yes (2026-08-03) - four tests, each driving a shipped main([...])`.
2. Give it a selector that is red.
3. Run `verify_ac.py run --id <id>`.
4. The line becomes the marked `no` and the author's annotation exists nowhere - not in the file, not in `recorded_reasons`.

## Proposed Fix

Carry the existing reason through the downgrade - `no (<date>) - <the downgrade note>; was: <the recorded reason>` - so the derived verdict records what it replaced rather than erasing it, exactly as the flip's `old_state` now does. Pin both directions: a positive verdict carrying a reason keeps it across a red run, and one carrying none is unchanged.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0733 established that a derived verdict never overwrites a recorded one, and enforced it on the green path.
- [ ] **AC2** The proposed fix lands, pinned by a test: Carry the existing reason through the downgrade - `no (<date>) - <the downgrade note>; was: <the recorded reason>` - so the derived verdict records what it...

## Impact

The unit's own principle, enforced on one branch and broken on the other, which is the shape that makes a rule untrustworthy: a reader who learns that a recorded note survives a green run will reasonably assume it survives a red one. Fifteen corpus lines are now in reach of the path that discards them, where before the widening none was.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | sdlc-studio | Filed |
