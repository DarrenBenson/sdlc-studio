# BG0566: npm run lint:fix destroys an artefact whose title contains a dunder: markdownlint infers underscore emphasis and rewrites every metadata line, and the schema validator then cannot find a Status

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .markdownlint.json, tools/lint-style.sh, tools/tests/test_markdown_style.py, tools/tests/test_lint_style.py
> **Evidence:** Hit while filing BG0564 in RUN-01KZM49Y, 2026-08-10. Its title contained `__init__.py`. markdownlint's MD050 read the surrounding underscores as strong emphasis, inferred `underscore` as the file's style, and `--fix` rewrote every `> **Status:**` to `> __Status:__`. `validate.py check` then reported `[no-status] no > **Status:** metadata line found` on an artefact the tool itself had just rewritten. Restoring the asterisks makes markdownlint fail again on the same file, so the two guards are in a stable loop with no fixed point until the dunder is backticked.
> **Verification depth:** functional (unit: 12 cases over the shipped style guard and 4 over the two markdownlint configs, every fixture under `tempfile`; mutation: 5 declared mutants applied to the config and the guard, each killed by its own criterion's verifier, with bytecode purged between runs; live: the destruction reproduced on a temp fixture before the fix and confirmed gone after it, and the whole tracked corpus measured clean under the new lane)
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

> **Grooming note - the filed criteria could not all be true at once.** AC1 and AC2 asked for
> an artefact carrying a BARE dunder to survive `--fix` unchanged AND be lint-clean afterwards.
> Measured on a temp fixture with `MD050: {style: asterisk}` applied: the metadata block does
> survive, and `--fix` then rewrites the H1's `__init__.py` to `**init**.py` instead. Pinning
> MOVES the destruction rather than removing it, because a pinned style is still a style
> `--fix` enforces. The only spelling both guards leave alone is a code span. So the fix is
> two-part - pin the style so the SCHEMA can never be flipped, and refuse the bare token before
> `--fix` can reach it - and the criteria below say which half each one holds.
>
> The tool in the filed text is `markdownlint-cli2`; this repo runs `markdownlint-cli` against
> `.markdownlint.json`, with `.claude/skills/sdlc-studio/.markdownlint.json` extending it. The
> criteria name what ships.

### AC1

- **Given** an artefact whose H1 carries a bare `__init__.py` and whose metadata block is the
  usual `> **Status:**` / `> **Severity:**` / `> **Points:**` lines, in a `tempfile` directory
- **When** `markdownlint --fix` is run over it from the repo root, with no `--config` - the root
  markdown lane's own invocation, so the config is resolved by markdownlint's discovery rather
  than by the test
- **Then** every metadata field still reads back through the shipped schema reader
  (`sdlc_md.extract_field`), and no `__Status:__` appears in the file.

- **Verify:** pytest tools/tests/test_markdown_style.py -k a_bare_dunder_no_longer_flips_the_metadata_block_to_underscores
- **Verified:** yes (2026-08-11)
- **Mutant:** in `.markdownlint.json`, drop the `MD050` entry. The style is inferred from the
  H1's dunder again, `--fix` rewrites all three metadata lines, and `extract_field` returns
  None on a file the tool itself just wrote.

### AC2

- **Given** the SAME artefact and the SHIPPED payload's config, which `extends` the root one -
  the config the second markdown lane passes explicitly, and the one most of the corpus is
  linted under
- **When** `--fix` is run with `--config` naming it
- **Then** the metadata block reads back through the schema reader unchanged. The pin is
  INHERITED, not restated: a second copy in the payload config is a second thing to drift.

- **Verify:** pytest tools/tests/test_markdown_style.py -k the_payload_config_inherits_the_pin_it_does_not_restate_it
- **Verified:** yes (2026-08-11)
- **Mutant:** in `.claude/skills/sdlc-studio/.markdownlint.json`, restate `MD050` as
  `"consistent"`. `extends` merges rather than replaces, so the nearer value wins and the
  payload lane infers again while the root config stays pinned and AC1 stays green.

### AC3

- **Given** a document that uses underscore strong emphasis CONSISTENTLY, so an INFERRED style
  agrees with it and reports nothing - the only fixture that separates "pinned to asterisk" from
  "MD050 switched off", since a mixed document is reported either way, only on different lines
- **When** it is linted under the root config and under the payload config
- **Then** both report `MD050` and exit 1.

- **Verify:** pytest tools/tests/test_markdown_style.py -k underscore_strong_emphasis_in_prose_is_still_reported
- **Verified:** yes (2026-08-11)
- **Mutant:** in `.markdownlint.json`, set `"MD050": false` instead of pinning the style.

### AC4

- **Given** markdown carrying a bare `__x__` pair outside a code span and outside a fenced block
- **When** `tools/lint-style.sh` runs over the tree
- **Then** it exits 1, names the file and line, and prints the backticking remedy - so the token
  is refused BEFORE anything runs `--fix` over it. This is the half AC1's pin does not cover:
  with the style pinned, `--fix` rewrites `__init__.py` to `**init**.py` instead.

- **Verify:** pytest tools/tests/test_lint_style.py -k a_bare_dunder_pair_in_a_heading_is_refused_before_fix_can_reach_it
- **Verified:** yes (2026-08-11)
- **Mutant:** in `tools/lint-style.sh`, drop the `status=1` from the bare-dunder branch, leaving
  a lane that reports and never refuses.

### AC5

- **Given** the three shapes that carry a double underscore and are NOT emphasis: a dunder
  inside a fenced block (every best-practice page shows `if __name__ == "__main__":`), a lone
  `___` run (the persona questionnaire's answer blank - measured as 12 of the 12 corpus lines
  carrying `__` outside code), and an intraword pair such as `mcp__a__b`, which CommonMark gives
  no emphasis meaning and markdownlint reports nothing on
- **When** each is linted
- **Then** none is flagged, and the artefact metadata block alone is clean. A lane keyed on `__`
  rather than on a bounded PAIR would have arrived red against the tree it guards.

- **Verify:** pytest tools/tests/test_lint_style.py -k a_lone_underscore_run_is_not_a_pair_and_is_not_flagged
- **Verified:** yes (2026-08-11)
- **Mutant:** in `tools/lint-style.sh`, relax the dunder pattern to a bare `__`, or delete the
  fenced-block skip from its awk pass.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.markdownlint.json`, drop the `MD050` entry so the strong style is inferred per file again | |
| AC2 | in the payload config, restate `MD050` as `"consistent"` so the pin is not inherited | |
| AC3 | in `.markdownlint.json`, set `"MD050": false` rather than pinning the style | |
| AC4 | in `tools/lint-style.sh`, drop the `status=1` from the bare-dunder branch | |
| AC5 | in `tools/lint-style.sh`, relax the dunder pattern to a bare `__`, or delete the fenced-block skip | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Filed |
| 2026-08-11 | sdlc-studio | Criteria regroomed against a measured reproduction: pinning alone moves the destruction to the title, so a second half refuses the bare token. Affects corrected to the config and test paths this repo actually ships |
