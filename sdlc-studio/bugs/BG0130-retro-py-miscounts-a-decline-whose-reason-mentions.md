# BG0130: retro.py miscounts a decline whose reason mentions an artefact id as filed

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py

## Summary

In retro.py `dispositions_in`, `ARTEFACT_ID_RE` is checked before `DECLINED_RE`, so a row like 'declined: belongs to RFC0034 (CR0257/CR0259)' is classified as FILED (it contains CR0257) rather than DECLINED. The finding is still counted as dispositioned, so the gate is unaffected - but the filed/declined tally is wrong. Found by dogfooding retro.py on RETRO0023, which reported '2 filed, 1 declined' for 1 filed + 2 declined.

## Steps to Reproduce

A retro Actions-raised row 'declined: <reason mentioning CRxxxx>'. retro.py validate/dispose reports it as filed. `dispositions_in` checks `ARTEFACT_ID_RE.search(disp)` before `DECLINED_RE.match(disp)`; an explicit 'declined:' prefix should win.

## Proposed Fix

Check `DECLINED_RE` (anchored '^declined:') BEFORE `ARTEFACT_ID_RE` - an explicit decline is a decline even if its reason cites an id. Add a test: 'declined: see CR0257' classifies as declined (LL0010).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
