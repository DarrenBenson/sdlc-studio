# BG-0012: TSD lint:links gate is skill-scoped, so the sdlc-studio/ artifact corpus is never link-checked (25 broken anchors slip through)

> **Status:** Open
> **Severity:** Medium
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

The TSD presents lint:links as a corpus-wide gate guaranteeing all anchors resolve, but check_links.py defaults to the skill subtree and the npm script passes no --root, so the ~47-file artifact corpus (with 25 broken anchors) is never checked.

## Problem

tsd.md:175 '100% of *.md pass', tsd.md:42 'resolvable links on every commit' over 'all markdown'. But tools/check_links.py:24 DEFAULT_ROOT = '.claude/skills/sdlc-studio' and the lint:links npm script passes no --root, so only the skill subtree is checked. Pointing the same checker at --root sdlc-studio surfaces 25 broken anchors (incl prd.md:287 reference-outputs.md#traceability and the persona anchors). markdownlint runs repo-wide, so the link checker is the lone skill-scoped gate.

## Proposed Fix

Either qualify the TSD link-integrity claim to 'intra-skill markdown only' and state the artifact corpus is not link-checked, or extend the gate with a lint:links:artifacts step invoking check_links.py --root sdlc-studio so the existing broken anchors fail CI as the TSD already implies.

## Evidence

tsd.md:175 'Every path.md#anchor reference resolves' vs check_links.py:24 DEFAULT_ROOT='.claude/skills/sdlc-studio' and 'check_links.py --root sdlc-studio' reporting 'Broken markdown anchor links (25)'

## Impact

The TSD asserts a structural invariant CI does not enforce over the documents this project ships as artifacts; 25 broken anchors live undetected and the link-integrity traceability is overstated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: tsd) |
