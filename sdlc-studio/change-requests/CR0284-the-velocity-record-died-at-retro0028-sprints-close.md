# CR-0284: The velocity record died at RETRO0028: sprints close 'not-yet-captured', the enforced close-down never checks the accuracy/velocity write, and plans still quote the 25k seed whose only out-of-sample test failed at 0.44x

> **Status:** Proposed
> **Priority:** High
> **Type:** process
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/retro.py, sdlc-studio/retros/VELOCITY.md, .claude/skills/sdlc-studio/hooks/close_guard.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

VELOCITY.md's header mandates the tokens-per-point rate be 're-measured every sprint from this file' and warns a written-down constant 'is an article of faith within two sprints' - yet its last row is RETRO0028 (2026-07-15) while every retro since closed without one. RETRO0028 is the only out-of-sample test of `TOKENS_PER_POINT`=25000: actuals ran 2.26x the forecast (56,407 tokens/pt, ratio 0.44x), and subsequent plans keep forecasting at the ~25,000 seed regardless. The loop broke at exactly the LL0027 point: CR0278 shipped `accuracy --tokens N --write` but RETRO0039-0041 all closed with 'Tokens: not-yet-captured' because `close_owed.py`'s `covered_ids()` only checks that some retro's Batch names the units - no accuracy/velocity condition exists anywhere in `close_owed.py` or hooks/`close_guard.py.` The estimator is unfalsifiable again, in the way the file's header says it became twice before. The panel notes the '13 sprints' framing is inflated (the post-mechanism window is RETRO0038-0041) but the enforcement gap and unrecorded window are real and untracked (CR0273 Superseded, CR0278 mechanism-only).

## Impact

VELOCITY.md's header mandates the tokens-per-point rate be 're-measured every sprint from this file' and warns a written-down constant 'is an article of faith within two sprints' - yet its last row is RETRO0028 (2026-07-15) while every retro since closed without one.

## Acceptance Criteria

- [ ] The close-down enforcement (`close_owed` or the retro close gate) refuses/flags a sprint close whose accuracy/velocity write did not run when a token total is supplyable, with a recorded-override escape
- [ ] VELOCITY.md gains rows (or explicit unmeasured entries) for the closed sprints since RETRO0028 where totals are recoverable
- [ ] Plan output that quotes the tokens-per-point rate states its provenance (seed vs measured) and the RETRO0028 out-of-sample result rather than presenting the 25k seed as calibrated

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
