# CR-0731: Make PyYAML a required dependency, refused at install and at the prerequisite check

> **Status:** Complete
> **Supersedes:** CR0714
> **Decomposed-into:** EP0368
> **Parent:** RFC0066
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** install.sh, install.ps1, docs/INSTALL.md, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/gate.py, sdlc-studio/prd.md, sdlc-studio/trd.md, README.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** RFC0066 decision of 2026-11-17, operator ruling D0505
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T17:15:24Z

## Summary

RFC0066 is decided: PyYAML becomes required. Today a project whose config exists but cannot be read, because PyYAML is absent, has every gate it switched on fall back to the shipped default with one warning and an unchanged exit code. The operator ruled that the installer and the prerequisite check refuse without PyYAML, and that the PRD and TRD drop the claim that the skill needs the standard library only. CR0714, which asked for the TRD to record the stand-down, is answered by this ruling and should be reconciled with it when refined.

## Impact

A consuming project on a machine without PyYAML runs with its opted-in gates disarmed and is told so only by a warning. After this change that machine is refused at install or at the first gate, and the project's own notes on prerequisites must name PyYAML.

## Acceptance Criteria

- [ ] The installer refuses, naming PyYAML and how to install it, on a machine where it cannot be imported
- [ ] The gate prerequisite check and every gate-bearing command exit non-zero when PyYAML is absent, and no command reads a present config as defaults
- [ ] The PRD and TRD no longer claim a standard-library-only runtime, and the TRD records the ruling as an ADR
- [ ] The TRD threat model carries a row for a missing or tampered PyYAML, and a test under tools/tests pins the TRD wording (carried from CR0714, closed as superseded by this request)
- [ ] The release notes for the next version name the new requirement as a breaking change for machines without PyYAML

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
