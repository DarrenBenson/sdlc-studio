# BG0618: a repair's evidence is split on a bare semicolon and the remainder is SILENTLY DROPPED, so the review ledger records less than the author wrote

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 8; plan rows 8; executed 8; killed 8; survived 0; not-run 0; entry point 1 of 8 criteria through the shipped CLI, 7 in-process | fp f31c44f73935 ]] (eight criteria over the two channels that share this shape, each with its own mutant executed and killed: the separator, the separator narrowed to nothing, the write-time refusal, the same repair applied to the issues channel only, the structured file route, a value ending in a real backslash, the Python floor, and the read-path report. THREE of these came from review or from my own re-execution finding a mutant alive: AC5 drives the SHIPPED CLI rather than the library, because its first cut called `closures_from_document` directly and the mutant that deletes the CLI's JSON branch survived it - the wiring is the half a library test cannot see; AC7's first verifier used `ast.parse(feature_version=(3, 10))`, which gates grammar rather than f-string tokenisation and so accepted on 3.14 the very syntax 3.10 rejects; and AC6 exists because an escapable separator needs an escapable escape)
> **Points:** 3
> **Depends on:** BG0621
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Hit repeatedly while recording the RUN-01M0WCCG repair round on 2026-08-25, where several closures were rejected or partially recorded until every semicolon was removed from the prose. Root cause isolated by executing `parse_closures` directly on 2026-08-26 and measuring the lost text. Parser quoted from critic.py:903 and 909-910.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`parse_closures` splits the `closed` text on a bare `;` (critic.py:903) and then discards any chunk that has no ` -> ` in it (critic.py:909-910, `if not finding or not evidence: continue`). There is no escaping, no quoting, and no warning. So a closure whose EVIDENCE contains a semicolon is truncated at that semicolon and everything after it vanishes from the durable record without a word. Proven by execution on 2026-08-26: the input `the guard fires -> fixed in sprint.py; the tests now cover the epic case, and the mutant was executed and killed` parses to ONE closure whose evidence is `fixed in sprint.py`, and 73 characters - the half that names the actual proof - are gone. The docstring states the same channel shape is used by `--issues`, so a verdict's findings have the identical exposure. The `--closed-file` path exists precisely so prose can be carried verbatim off disk rather than through a shell, and it protects backticks and `$(` while leaving this wide open.

## Steps to Reproduce

1. Write a repair closure whose evidence contains a semicolon, in a file. 2. `critic.py repair --unit <id> --author <who> --closed-file <file>`. 3. Read sdlc-studio/reviews/repair-record.md: the evidence stops at the first semicolon. Nothing is printed, nothing is refused, and the exit code is 0. Reproduced in-process against `parse_closures` directly, so the loss is in the parser rather than in any shell.

## Proposed Fix

Two changes, and the second matters more than the first. Give the channel a way to carry a semicolon - the file path already reads structured input off disk, so accept a JSON list of closures there and stop re-parsing prose into records. And in every case, REFUSE a chunk that has no ` -> ` rather than dropping it: a fragment the parser cannot understand is either an author error or a split that should not have happened, and both are worth a refusal. Silence is the part that makes this dangerous, not the split.

## Acceptance Criteria

- [x] **AC1** Given a closure whose EVIDENCE contains a semicolon, when the repair is recorded and read back, then the evidence is stored WHOLE - every clause the author wrote reaches the record, modulo the ledger's own markdown escaping (`_` and `|`, which `_clean` applies deliberately for MD037 and table safety) - rather than being truncated at the first semicolon
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureChannelTests::test_evidence_carrying_a_semicolon_is_stored_whole
  - **Verified:** yes (2026-08-26)
- [x] **AC2** Given a closure whose evidence contains NO semicolon, when it is recorded, then it parses exactly as it does today - the paired control, so carrying a semicolon does not become the only shape the channel accepts
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureChannelTests::test_ordinary_evidence_still_parses_unchanged
  - **Verified:** yes (2026-08-26)
- [x] **AC3** Given a chunk the parser cannot read as `<finding> -> <evidence>`, when it is WRITTEN, then the write is REFUSED by name - and when an existing row is READ, it is REPORTED and not raised. The silence is the defect, but refusing on the read path crashes `conformance.py check` inside `repair_state`: 67 chunks already on disk across 11 units lack the separator, five of them among the units this run must backfill
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureChannelTests::test_an_unparseable_chunk_is_refused_rather_than_dropped
  - **Verified:** yes (2026-08-26)
- [x] **AC4** Given a `--issues` string carrying a semicolon inside one finding, when a verdict is recorded, then that finding survives whole - the channel BG0618 is about is shared, so a fix that repairs only the repair path leaves the verdict path corrupting the same way
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureChannelTests::test_the_issues_channel_carries_a_semicolon_too
  - **Verified:** yes (2026-08-26)
- [x] **AC5** Given a `--closed-file` holding a JSON list of `{finding, evidence}` objects, when the repair is recorded, then each evidence string reaches the record whole however many semicolons it contains - structured input has NO delimiter, so nothing a reviewer writes can be read as one. The escape above keeps the flag form working; this is the repair the artefact's own Proposed Fix asks for
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureChannelTests::test_a_json_closure_document_needs_no_separator_at_all
  - **Verified:** yes (2026-08-26)
- [x] **AC6** Given evidence ending in a real backslash, when the closures are parsed, then the item after it is NOT swallowed - an escapable separator needs an escapable ESCAPE, or a lookbehind cannot tell a backslash that escapes the semicolon from one that is itself escaped, and nothing refuses the merge
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureChannelTests::test_a_value_ending_in_a_backslash_does_not_swallow_the_next_item
  - **Verified:** yes (2026-08-26)
- [x] **AC7** Given this project's declared Python floor of 3.10, when `critic.py` is parsed at that feature version, then it parses - a backslash inside an f-string EXPRESSION is legal only from 3.12, and `import critic` raising takes the conformance lane, `sprint` and `transition` with it on the interpreter Ubuntu 22.04 ships. CI pins 3.12, so nothing else looks
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureChannelTests::test_the_module_parses_on_the_declared_python_floor
  - **Verified:** yes (2026-08-26)
- [x] **AC8** Given an unreadable row already on disk, when it is READ, then it is REPORTED by name on stderr and not raised - 67 such chunks exist across 11 units so raising would crash every reader, but skipping in silence keeps the half of this defect that made it dangerous
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClosureChannelTests::test_an_unreadable_row_is_reported_when_read
  - **Verified:** yes (2026-08-26)

## Impact

The repair record is what a reviewer reads to judge whether a REJECT was genuinely answered, and `repair_state` computes complete-versus-partial from these rows. Recording less evidence than the author supplied, with no signal, corrupts the one artefact whose job is to prove a finding was closed - and it does so most often on exactly the evidence worth having, because a substantial closure is the kind that runs to two clauses. Graded High against the rubric: the feature is broken and there is no workaround the tool ever tells you about. An author cannot avoid a semicolon they do not know is fatal. Re-triage it if the panel disagrees, as BG0604 was.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `critic.py`, replace `split_items` with a bare `text.split(";")` so an escaped semicolon is treated as a separator again | Given a closure whose EVIDENCE contains a semicolon, when the repair is recorded and read back, then the evidence is stored WHOLE - every clause the author wrote reaches the record, modulo the ledger's own markdown escaping (underscores and pipes, which `_clean` rewrites deliberately for MD037 and table safety) - rather than being truncated at the first semicolon |
| AC2 | in `critic.py`, narrow `split_items` to return the whole string as one item, so an ordinary two-closure string stops parsing | Given a closure whose evidence contains NO semicolon, when it is recorded, then it parses exactly as it does today - the paired control, so carrying a semicolon does not become the only shape the channel accepts |
| AC3 | in `critic.py`, delete the `unreadable_closures` refusal from `record_repair`, so an unreadable chunk is dropped silently again | Given a chunk the parser cannot read as `<finding> -> <evidence>`, when it is WRITTEN, then the write is REFUSED by name - and when an existing row is READ, it is REPORTED and not raised. The silence is the defect, but refusing on the read path crashes `conformance.py check` inside `repair_state`: 67 chunks already on disk across 11 units lack the separator, five of them among the units this run must backfill |
| AC4 | in `critic.py`, replace `split_items` in `parse_findings` with a bare `text.split(";")`, repairing only the closure channel | Given a `--issues` string carrying a semicolon inside one finding, when a verdict is recorded, then that finding survives whole - the channel BG0618 is about is shared, so a fix that repairs only the repair path leaves the verdict path corrupting the same way |
| AC5 | in `critic.py`, delete the JSON branch from `cmd_repair` and read every `--closed-file` as prose | Given a `--closed-file` holding a JSON list of `{finding, evidence}` objects, when the repair is recorded, then each evidence string reaches the record whole however many semicolons it contains - structured input has NO delimiter, so nothing a reviewer writes can be read as one. The escape above keeps the flag form working; this is the repair the artefact's own Proposed Fix asks for |
| AC6 | in `critic.py`, replace `split_items`' scanner with the `(?<!\\);` lookbehind, so an escaped backslash reads as escaping the separator | Given evidence ending in a real backslash, when the closures are parsed, then the item after it is NOT swallowed - an escapable separator needs an escapable ESCAPE, or a lookbehind cannot tell a backslash that escapes the semicolon from one that is itself escaped, and nothing refuses the merge |
| AC7 | in `critic.py`, move an escape back inside an f-string expression - a backslash there is legal only from Python 3.12, and the floor is 3.10 | Given this project's declared Python floor of 3.10, when `critic.py` is parsed at that feature version, then it parses - a backslash inside an f-string EXPRESSION is legal only from 3.12, and `import critic` raising takes the conformance lane, `sprint` and `transition` with it on the interpreter Ubuntu 22.04 ships. CI pins 3.12, so nothing else looks |
| AC8 | in `critic.py`, delete the warning from `parse_closures` and `continue` past an unreadable row in silence | Given an unreadable row already on disk, when it is READ, then it is REPORTED by name on stderr and not raised - 67 such chunks exist across 11 units so raising would crash every reader, but skipping in silence keeps the half of this defect that made it dangerous |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
