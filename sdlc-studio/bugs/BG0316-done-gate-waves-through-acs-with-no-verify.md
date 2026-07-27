# BG0316: Done gate waves through ACs with no Verify line while blocking honestly-declared manual ACs

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

A story whose ACs carry no Verify: line reaches Done completely ungated, while one declaring 'Verify: manual' is blocked until each AC carries Verified: yes - omission is strictly cheaper than declaration, inverting the gate's incentive, and the transition gate disagrees with gate.py's release lane, which treats an unspecified AC as blocking, so a story closed Done all sprint fails only at tag time.

## Steps to Reproduce

Evidence (`_done_verify_gate` / `_story_has_executable_acs`, lines 106-159 (early return at 158-159)): Reproduced: a fixture story with 2 ACs and zero Verify lines transitions to Done rc=0; adding one 'Verify: manual' line blocks it rc=1. transition.py:158-159 returns None when no executable ACs exist; gate.py `_verify_acs`:1458-1459 fails and names unspecified ACs.

## Proposed Fix

Make `_done_verify_gate` treat a verifier-less AC the way gate.py does - block the Done transition (or require the same Verified: yes evidence as manual) so omission is never cheaper than honest declaration.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Triaged vs BG0300 (already-delivered advisory): distinct - BG0300's fix blocks a bare manual AC; this bug is the adjacent gap that an AC with no Verify line at all is waved through, making omission cheaper than honest declaration. Stays Open. |
