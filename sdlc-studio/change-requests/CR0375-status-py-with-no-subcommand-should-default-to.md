# CR-0375: status.py with no subcommand should default to the pillars dashboard instead of erroring

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The natural first call is bare status.py (mirroring '/sdlc-studio status'); it exits 2 with an argparse usage error demanding a cmd. Every other read of this surface starts from the pillars dashboard, so the bare call has one obvious meaning. Cost one retry at the start of the RUN-01KXZQF0 planning session; trivially, every new agent onboarding a project pays the same retry.

## Impact

first-contact ergonomics for agents and operators; one retry per session start adds up across every consuming project

## Acceptance Criteria

- [ ] python3 status.py with no subcommand prints the pillars dashboard and exits 0, exactly as status.py pillars does
- [ ] explicit subcommands and their flags behave unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
