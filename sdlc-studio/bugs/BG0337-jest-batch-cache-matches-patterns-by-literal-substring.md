# BG0337: Jest batch cache matches patterns by literal substring where jest -t is a regex, so cached and authoritative verdicts ca

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The cache resolver claims to mirror jest -t but uses Python substring containment ('pat in a["name"]') where jest treats -t as a testNamePattern regex; a metacharacter-bearing pattern that literally occurs in some passing assertion name yields a green cached verdict computed over a different test set than jest would select, and under --release the batch cache substitutes for the authoritative run in a blocking gate lane.

## Steps to Reproduce

Evidence (`resolve_jest_from_cache`, lines 1132-1145): Confirmed at `verify_ac.py` 1132-1145: docstring says 'mirroring jest -t', implementation is substring containment; the pytest cache path by contrast refuses anything but a bare node id.

## Proposed Fix

Match with re.search(pat, name) to mirror jest's testNamePattern semantics, and on re.error (invalid regex) return None so the caller falls back to the authoritative per-AC jest subprocess.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
