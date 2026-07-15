# BG0150: project upgrade does not stamp the project version and skips open RFCs/CRs/epics/stories

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/project_upgrade.py
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Operator-reported: running project upgrade on an existing consuming project added personas but left the project version number missing, and did not review or update any open RFCs, CRs, epics or stories. Behaviour observed on a consuming project; investigate `project_upgrade`'s version-stamp step.

## Steps to Reproduce

Run project upgrade on a consuming project that predates the current version and carries open RFCs/CRs/epics/stories.

## Proposed Fix

Stamp/refresh the recorded project version during upgrade (so skill-update/migrate can detect it). The broader open-artefact sweep is the migrate RFC's scope; this bug is scoped to the version stamp.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
