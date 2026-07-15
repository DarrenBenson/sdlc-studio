# BG0149: artifact.py silently drops --points on a story, so the canonical creator makes a story the grooming gate always rejects

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** major
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

artifact.py new --type story accepts --points but never writes a Points field; the story template has no Points placeholder. The canonical creator therefore produces a delivery unit the grooming gate always rejects and whose parent epic rolls up to 0 points.

## Steps to Reproduce

artifact.py new --type story --epic EP0033 --points 5 --title '...' creates a story with NO Points line; `read_points()` returns None; sprint plan reports 'lacks: Points'; reconcile computes the parent epic Derived Point Total as 0. Found dogfooding CR0271 decomposition: all 5 stories filed with --points came out unpointed.

## Proposed Fix

artifact.py must write Points on a story/bug from --points, using the same `sdlc_md` definition the gate reads. The LL0016 pair of BG0148: creator and grooming gate must agree on a delivery unit shape. Bundle with BG0148 so artifact.py writes the RIGHT sizing field per type.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
