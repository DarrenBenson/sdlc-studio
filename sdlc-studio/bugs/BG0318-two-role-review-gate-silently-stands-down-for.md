# BG0318: Two-role review gate silently stands down for every schema-v3 (ULID) unit when review.two_role_after is set

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

`sdlc_md.id_number` returns None for a v3 ULID id, making `two_role_applies` False for every ULID unit, so on a schema-v3 project with `review.two_role_after` set both the evidence half and the sign-off half default to True unchecked - the forward-only cutoff fails open on exactly the newest units it exists to cover, with no warning, contradicting the non-negotiable that units past the cutoff hold at Review.

## Steps to Reproduce

Evidence (`_done_stages` lines 215-218 and `detect_conformance` lines 407-411): conformance.py:215-217 requires `rid_num` is not None for the gate to apply, then line 218 defaults both halves True; lib/`sdlc_md.py`:1252-1263 documents `id_number` returning None for ULIDs; verified by execution: `id_number(`'US-01JQK3F8') is None. Contrast `adopt_after` handling at lines 417-418, which fails safe on the same None.

## Proposed Fix

Fail closed: when `two_role_after` is set and `id_number` returns None, apply the two-role requirement to the unit (ULID ids are by construction newer than any numeric cutoff), or refuse the numeric-cutoff config on a v3 workspace with a clear error.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
