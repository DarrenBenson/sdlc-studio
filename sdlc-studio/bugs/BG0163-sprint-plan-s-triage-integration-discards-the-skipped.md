# BG0163: sprint plan's triage integration discards the skipped/unreadable count - a dropped backlog file is silent in the ceremony whose story title promises 'drops logged'

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

`backlog_triage.triage`'s contract (docstring:271-272) returns findings AND a scanned/skipped count 'so a caller (plan, status) can surface them and a drop is never silent'. status.py honours it ('N artefact(s) unreadable - could not be checked'); sprint plan - the command the ceremony was built into (EP0047) - reads only ["findings"] at sprint.py:1197 and throws `skipped` away, and `_render_triage` prints no section when findings are empty, so an unreadable backlog artefact reads as a clean plan - the silent-truncation-reads-as-clean failure the module's header says it exists to prevent. RFC0037's design explicitly requires drops logged in the plan ceremony; US0170's title promises it but neither AC covers it, so the omission passed Done unchecked (LL0016/LL0008/LL0013/LL0027 - the full set). Committed EP0047 work, not in-flight. Verified 3x.

## Steps to Reproduce

Make one backlog artefact unreadable (e.g. invalid header); run sprint plan - the triage section shows nothing about the drop (or no section at all), while `status` reports 'N artefact(s) unreadable'.

## Proposed Fix

`_batch_triage` propagates `skipped`; the plan renders 'N artefact(s) unreadable - not triaged' even when findings are empty; add a drops-logged case to TriageInPlanTests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
