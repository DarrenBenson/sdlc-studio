# CR-0251: verify_ac run: the natural --file flag does not exist (friction: it is --story)

> **Status:** Proposed
> **Priority:** P4
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py

## Summary

Friction hit while dogfooding the review: '`verify_ac.py` run --file story.md' errors (unrecognized arguments); the flag is --story (with --dir and --id the other two forms). --file is the name an agent reaches for first. The error is fail-loud and lists valid subcommands, which is good, but the flag naming is a discoverability snag. Minor.

## Impact

An agent or operator running a single-story verify guesses --file, hits an argparse error, and has to read --help. Small friction, repeated.

**Effort:** S

## Acceptance Criteria

- [ ] `verify_ac.py` run accepts --file as an alias for --story (or the help/docs prominently name --story where an example would use a file). Verify: python3 scripts/`verify_ac.py` run --file X --dry-run does not error on the flag

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
