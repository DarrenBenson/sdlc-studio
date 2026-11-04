# CR-0660: gate.py --release takes about 100 minutes on a workstation, nearly all of it the verify lane executing every Done story's criteria serially

> **Status:** Complete
> **Decomposed-into:** EP0296
> **Priority:** Medium
> **Type:** Feature
> **Date:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:07:30Z

## Summary

At the 6.2.0 release (2026-11-02), `gate.py --release` took 4,608 s, 6,217 s and 6,975 s on three runs, of which the verify lane was 4,447 s, 6,048 s and 6,582 s. Every red criterion it found had to be fixed and the whole gate re-run, so finding one slow test cost another 100 minutes. 6.2's stated priority is efficiency.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Options 1 and 2 together: parallel on the gate host. Option 3 risks a stale green, which the verify lane exists to prevent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Raised |
