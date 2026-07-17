# CR-0338: A global doc-coverage failure reports as N per-unit 'missing documented', not one global-floor finding

> **Status:** In Progress
> **Decomposed-into:** EP0072
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The 'documented' conformance stage is a repo-global floor (like 'reconciled'): if doc-coverage has ANY undocumented item, EVERY unit reports 'missing documented'. During the RUN-01KXQH64 close, one uncatalogued command (audit in the Type Reference but not help/help.md) made conformance report 118 non-conformant units - reading as 118 broken units when it was one doc gap. The signal is buried and misleading.

## Impact

An operator or agent reading a gate failure sees N (here 118) non-conformant units and cannot tell it is one global doc-coverage miss; wastes diagnosis time and looks like a large regression.

## Acceptance Criteria

- [ ] When the 'documented' stage fails ONLY because of the global doc-coverage floor, conformance attributes it once as a global finding (naming the undocumented item) rather than fanning 'missing documented' across every unit; per-unit 'missing documented' is reserved for genuinely per-unit gaps.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
