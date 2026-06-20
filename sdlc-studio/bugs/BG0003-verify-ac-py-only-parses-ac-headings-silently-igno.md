# BG-0003: verify_ac.py only parses ### AC headings, silently ignoring the bullet AC style the rest of the skill accepts, so the release gate passes vacuously

> **Status:** Open
> **Severity:** Critical
> **Reporter:** Adversarial Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

parse_story() matches only AC_HEADING_RE, so stories written in the blessed '- **AC1:**' bullet style yield zero AC blocks; their Verify lines never run and the story-completion AC gate passes silently with nothing verified.

## Problem

verify_ac.py parse_story uses AC_HEADING_RE ('### AC1: Title') as the sole AC trigger (verify_ac.py:44, :79). The shared lib defines AC_BULLET_RE and extract_ac_id honours both styles, and validate.py accepts bullet-style ACs (validate.py:101-110). A story authored as '- **AC1:** ... - **Verify:** ...' therefore yields zero AC blocks from verify_ac, so verify-report.json shows nothing and no Verify line runs. The story-completion cascade step 0 (reference-outputs.md:664) runs verify_ac.py and aborts only if an AC reports Verified: no or a failure; with zero ACs parsed there are no failures, so the gate passes silently on a story whose ACs were never verified - a false green on the only deterministic release-blocking check.

## Proposed Fix

Make parse_story() also recognise AC_BULLET_RE (reuse sdlc_md.extract_ac_id) so bullet-style ACs become ACBlocks whose Verify/Verified lines are parsed and run. Add a bullet-style fixture story to scripts/tests. Additionally emit an explicit 'no-ac-blocks' signal (non-zero or distinct status) so the cascade gate can distinguish 'all verified' from 'nothing to verify'.

## Evidence

.claude/skills/sdlc-studio/scripts/verify_ac.py:79 (AC_HEADING_RE.match is the sole AC trigger) vs lib/sdlc_md.py:120 extract_ac_id honouring both styles and validate.py:101-110 accepting bullet ACs

## Impact

The verify gate - the only executable AC enforcement and the headline differentiator vs binary checklists - is bypassed for an entire authoring style the rest of the skill blesses. Stories are marked Done with unrun acceptance criteria, defeating require_ac_verification. Quality risk critical.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism) |
