# BG0108: artifact.py schema-v3 skeletons fail their own validator (no Raised-by line)

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-11
> **Created-by:** sdlc-studio file

## Summary

On a `schema_version`:3 workspace, artifact.py new/batch creates artefacts without the '> **Raised-by:** Name; type; version' line that validate.py (authorship rule, ~L117) requires on every v3 artefact. Today's sdlc-bench decomposition birthed 31 artefacts that opened with ~130 validator errors; three authoring agents each independently rediscovered and hand-stamped the line. The deterministic creator must emit artefacts the deterministic validator accepts.

## Steps to Reproduce

1. In a workspace with sdlc-studio/.config.yaml `schema_version`: 3, run artifact.py new --type story --title X --epic <id>. 2. Run validate.py check. 3. Authorship error on the fresh skeleton.

## Proposed Fix

artifact.py stamps Raised-by at creation from --author (resolving type/version the same way transition.py does; default to the invoking agent identity when --author is absent).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Filed |
