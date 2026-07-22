# BG0266: The file verb over a directory is an always-passing prose verifier, and the markdown guard does not see it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by the round 3 adversarial reviewer of RUN-01KY5EJX and left unfixed when that run closed, so it is filed rather than carried in a commit message.

`file X.md` is refused by `lint_markdown_evidence` - a criterion verified by the existence of a markdown file proves someone created a file. `file docs/` is NOT refused, because the written token does not end in `.md` and the resolved reading treats the directory as its contents. The runner for the `file` verb is `test -e <path>`, so the verifier passes the moment the directory exists and passes forever after, regardless of what is in it or whether the behaviour was ever built.

It is the direct sibling of the refused form and strictly weaker evidence: `file X.md` at least names a specific document, while `file docs/` asserts that a directory exists. Both are prose evidence; only one is caught.

Note the shape, which is this project's recurring one rather than a new species. The guard was built and then repaired three times against `grep`, because `grep` was where the escapes were found, and the `file` verb was carried along by the same `_PROSE_VERBS` membership without anyone checking that the resolved reading means the same thing for it. Two verbs share a rule; only one of them was ever tested against it.

## Steps to Reproduce

1. Author an AC with `- **Verify:** file .claude/skills/sdlc-studio/help/` on a Draft story. 2. Run `verify_ac lint --story <file>`. Observed: exit 0, nothing refused. 3. Run `verify_ac run --story <file>`. Observed: the AC PASSES, because the built command is `test -e <dir>`. Expected: refused at lint time in the same manner as `file X.md`, since a directory of prose is not weaker evidence than one prose file, it is weaker still.

## Proposed Fix

Treat a `file` verifier whose target is a DIRECTORY as prose evidence when the files the runner would read under it are all markdown, using the same `_runner_files` walk the grep path already uses. Consider refusing `file <directory>` outright regardless of contents: `test -e` on a directory is satisfied by the directory existing, which is not evidence of any behaviour, and no legitimate criterion is expressed that way. Whichever is chosen, the `file` verb needs its own tests against the markdown rule rather than inheriting the grep path's coverage - it has none today, which is why this survived four rounds of work on the same function.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
