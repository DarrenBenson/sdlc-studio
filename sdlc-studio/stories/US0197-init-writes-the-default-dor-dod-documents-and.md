# US0197: init writes the default DoR/DoD documents and offers stack-derived tailoring criteria, applied only on acceptance and passing registry validation

> **Status:** Ready
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/help/init.md
> **Epic:** EP0067
> **Points:** 3

## User Story

**As** Trevor Hale (enterprise PM)
**I want** a new project to start with DoR/DoD documents plus a tailoring offer derived from its detected stack
**So that** the ready/done bar fits the project from day one instead of staying at generic defaults nobody hand-tailors

## Acceptance Criteria

### AC1: init writes defaults and offers, never auto-applies

- **Given** a fresh project whose stack (language, test framework, deploy surface) init can detect
- **When** `init.py` runs
- **Then** init writes the default documents and prints the tailoring offer with detected-stack-derived suggestions; nothing is applied without acceptance
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_init.py -k Tailor

### AC2: an accepted tailoring passes registry validation

- **Given** a tailoring offer the operator accepts
- **When** the tailored documents are validated
- **Then** The tailored result passes slice 1's registry validation (only registered check ids)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_init.py -k TailorRegistry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
