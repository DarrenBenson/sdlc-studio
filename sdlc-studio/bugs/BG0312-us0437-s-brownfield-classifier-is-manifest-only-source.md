# BG0312: US0437's brownfield classifier is manifest-only: source without a manifest classifies greenfield, and the verifier canno

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

AC2 promises brownfield for a repo 'that already contains source', but `classify_path` keys entirely off six manifest markers plus *.csproj, so a source-full repo without one (C/C++, Ruby, PHP, setup.py-only Python) classifies greenfield; the dedicated verifier only exercises pyproject.toml so it can never fail on the AC's own Given, and US0439's PRD stage then directs a real brownfield repo to the greenfield interview - the exact wrong fork the guided flow exists to avoid.

## Steps to Reproduce

Evidence (`classify_path`/`detect_stack`, lines 41-43, 77-83, 179-183; US0437 AC2 (line 30); `test_init.py`:312-318): init.py:183 'return "brownfield" if `detect_stack(...)` else "greenfield"' over the DETECT marker list only; reproduced: a repo with src/main.c and setup.py returns greenfield; the Verify test writes only pyproject.toml for its brownfield case.

## Proposed Fix

Add a fallback source-file census (extension scan) to `classify_path` when no manifest is found, and add a manifest-less brownfield case to GuidedInitTests so the AC's stated Given is actually exercised.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
