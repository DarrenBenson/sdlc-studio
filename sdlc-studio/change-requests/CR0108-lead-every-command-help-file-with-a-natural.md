# CR-0108: Lead every command help file with a natural-language 'You can just ask' block + enforce it

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

The skill is model-invoked, so plain language is the real interface, but the help files are command-centric - so a non-technical operator (the headline audience: a founder driving a full software-engineering team by asking) cannot see they can just say what they want. Add a top '## You can just ask' block to every command help file: a '| Just say... | Runs |' table mapping NL phrasings to that type's commands. help.md + getting-started.md carry a cross-cutting NL block. Enforce via a CI check so new help files keep the convention. Decisions taken: scope = per-type command help only (skip arguments.md/references.md); form = top 'You can just ask' table; enforcement = a check.

## Acceptance Criteria

- [x] Every help/*.md except the meta allowlist (arguments.md, references.md) carries a top '## You can just ask' section with a '| Just say... | Runs |' table (3-6 rows) mapping NL phrasings to that file's commands
- [x] help.md and getting-started.md carry a cross-cutting NL block (the front doors), framed for a non-technical operator
- [x] disclosure.py gains a 'help-missing-nl-block' finding for any non-meta help file lacking the block (allowlist: arguments.md, references.md); the gate keeps disclosure at 0 so the convention is enforced for new help files
- [x] unit test for the checker (present passes, absent flags, meta-allowlist exempt); a note in best-practices/claude-skill.md that help files lead with NL; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
