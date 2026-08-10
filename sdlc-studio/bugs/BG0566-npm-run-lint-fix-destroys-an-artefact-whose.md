# BG0566: npm run lint:fix destroys an artefact whose title contains a dunder: markdownlint infers underscore emphasis and rewrites every metadata line, and the schema validator then cannot find a Status

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .markdownlint-cli2.jsonc, tools/lint-style.sh, .claude/skills/sdlc-studio/scripts/tests/tests_markdown_style.py
> **Evidence:** Hit while filing BG0564 in RUN-01KZM49Y, 2026-08-10. Its title contained `__init__.py`. markdownlint's MD050 read the surrounding underscores as strong emphasis, inferred `underscore` as the file's style, and `--fix` rewrote every `> **Status:**` to `> __Status:__`. `validate.py check` then reported `[no-status] no > **Status:** metadata line found` on an artefact the tool itself had just rewritten. Restoring the asterisks makes markdownlint fail again on the same file, so the two guards are in a stable loop with no fixed point until the dunder is backticked.
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Two shipped guards disagree, and the disagreement destroys data rather than reporting it.

MD050 enforces a CONSISTENT strong-emphasis style per file and infers that style from the first occurrence. A bare `__init__.py` anywhere in a document is an occurrence, so the whole file is judged to be underscore-styled - and `--fix`, which `npm run lint:fix` runs and which the pre-commit hook recommends by name, converts every `**...**` in the file to `__..._`.

Every sdlc-studio artefact carries its metadata as `> **Status:**`, `> **Severity:**`, `> **Affects:**`. The schema parser matches asterisks. So one `lint:fix` on such a file silently unmakes the artefact: `validate` loses the Status, `reconcile` loses the index cell, and a terminal transition refuses on an artefact that was correct minutes earlier.

The trap is entirely ordinary. `__init__.py`, `__main__`, `__all__` and `--fix` are all things a Python project's bug titles contain, and the guidance to run `lint:fix` is printed by the hook on every markdown failure.

## Steps to Reproduce

1. File a bug whose title contains a bare `__init__.py`. 2. Run `npx markdownlint-cli2 --fix` on it, or `npm run lint:fix`, as the pre-commit hook's failure message suggests. 3. Every `> **Field:**` line becomes `> __Field:__`. 4. `validate.py check` reports `[no-status] no > **Status:** metadata line found`. 5. Restore the asterisks and markdownlint fails again on the same file - the two guards have no shared fixed point.

## Proposed Fix

The artefact's metadata is schema, not prose, so the style rule must not reach it. Either exclude the metadata block from MD050, or pin `style: asterisk` explicitly in the markdownlint config so nothing is inferred from a filename that happens to contain underscores. Pinning is the smaller change and removes the inference entirely, which is the actual defect - a per-file inferred style means one word in a title decides how the whole document is rewritten. Pin it with a fixture whose title carries a dunder, asserting the artefact survives `--fix` with its Status intact and that markdownlint is clean afterwards - both directions, since either alone has a trivial wrong answer.

## Acceptance Criteria

- [ ] **AC1** An artefact whose title contains a bare dunder survives `markdownlint-cli2 --fix` with every `> **Field:**` metadata line intact, asserted by parsing it back with the schema reader
- [ ] **AC2** The same artefact is markdownlint-clean after the fix, so the two guards have a shared fixed point rather than a loop
- [ ] **AC3** A document that genuinely uses underscore emphasis in prose is still reported, proving the style was pinned rather than the rule switched off

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Filed |
