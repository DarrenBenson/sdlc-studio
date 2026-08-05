# CR-0511: Low-severity bugs (consolidated)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-31
> **Consolidation:** low-severity-bugs
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Points:** 3
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

A themed consolidation of Low-severity findings that individually do not warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then action or reject as one.

## Impact

Each finding here is Low-severity on its own; the batch is triaged, then actioned or rejected as one. Left unconsolidated, the same findings would each mint an artefact and drown the real signal.

**Points:** 3

## Consolidated Findings

- **A repo-root file cannot be declared in Affects without a leading ./ and nothing says so**: `affects_files` does not read a bare root-level filename as a path, so `Affects: package-lock.json` parses to nothing and the grooming gate refuses the filing as UNGROOMED. `./package-lock.json` works. The refusal text explains that a prose phrase or bare word counts as no Affects at all, but never says that a legitimate repo-root file needs the `./`, so the author is told what is wrong without being told what to type.
- **close_preflight's RunStateError early return sets gate_ran but nothing pins it, and close_dry_run crashes on the same corrupt state**: Round-4 review, non-blocking. close_preflight has four returns; three now pin gate_ran and the RunStateError branch does not - hardcoding it to True there SURVIVES the full suite. The behaviour is correct today (a corrupt run state reports gate_ran False), so this is a coverage gap on a correct line rather than a live defect. Separately and pre-existing: with the same corrupt run state, `close_dry_run`'s `state = run_state.read(scratch) or {}` raises RunStateError uncaught, because the enclosing `try` carries only a `finally` and no `except`. cmd_close guards run-state faults before reaching the dry run, so it is unreachable from the CLI and bites only a direct library caller.
- **sprint breakdown has no --epic while sprint plan does, so the read-only census cannot be scoped the way the planner can**: `sprint plan` accepts `--epic EPxxxx` (repeatable) to scope a story batch to one or more epics. `sprint breakdown`, documented as reporting 'the same census read-only', does not: it exits 2 with 'unrecognized arguments'. So the safe read-only way to ask whether an epic's stories are groomed is unavailable, and the answer has to come from the writing command or from a hand-built worklist.

  Hit while checking whether four freshly refined epics were groomed before planning. The workaround was to hand-write a worklist file of twenty ids - which is the hand-rolling CR0515 exists to make visible, forced by a gap in a command pair that documents itself as symmetric.
- **goal-review record takes 'seat' in a fields-file but documents 'role' on the flag, and the refusal names neither spelling's fix**: `sprint goal-review record --seat SPEC` documents its format as 'role|achievable|what done means|one increment[|note]'. The `--fields-file` path for the same command requires each seat object to carry the key `seat`, not `role`. A document written from the flag's documentation is refused with 'a seat verdict in --fields-file has no seat role', which names the missing key ambiguously and does not say that the flag calls it something else.

  The fields-file path exists precisely so a seat note carrying shell metacharacters is stored verbatim, so it is the path a considered verdict takes - and it is the one whose key name is undocumented.
- **the suite-claim lane fires on a message that QUOTES a greenness claim rather than making one**: The commit-msg suite-claim lane matches the phrase anywhere in the message, so a commit DESCRIBING the defect refuses itself. Hit while filing BG0492, whose body reads: a scripts-only verdict satisfies a claim of "both suites green". The lane matched the quoted phrase and blocked the commit, though the message makes no claim about this commit's suite at all.

  Self-demonstrating, and the second time this repo has hit the shape - BG0301 was the shell-hazard detector firing on the artefact that documented it. A guard that cannot tell a claim from a quotation of a claim will refuse precisely the commits that write about it.
- **US0613's criterion names `sprint run`, which is not on the shipped command surface**: US0613 AC1 requires that `sprint plan` and `sprint run` print the toolchain runbook, and its story title asserts the same. There is no `run` verb: `sprint.py`'s parser offers plan, breakdown, close, boundary, report, preflight, goal-verdict, goal-review, reopen, stop, decision, batch, add-epic, appetite, review-batch and lane. The unit's own changelog fragment is more accurate than its criterion - it claims only `sprint plan`.

  So the criterion demanded behaviour of a command that does not exist, and passed anyway because its verifier was a source grep. The grep is repaired in 307ce91d and now drives `sprint plan` and reads its output; the criterion text is not, and it still promises a second command nobody can invoke.
- **the claim-drift ledger exemption names a file that does not exist while the real evidence ledger is still read as prose**: `_LEDGER_NAMES` exempts `evidence-record.md`, which exists nowhere in the tree. The repository's actual append-only evidence ledger is `sdlc-studio/reviews/critic-evidence.md`, and it is NOT exempt, so its rows are read as prose by the claim-drift lane. `command-audit.md` and `root-census.md` are record tables on the same reasoning and are also unlisted. One entry is inert and the ledger it was presumably meant to name is unprotected.
- **the link checker's label-column state leaks between tables, so one table's header decides how the next one is read**: `label_cols` is loop state that is not reset per table. A table whose first-column header matches neither vocabulary inherits the previous table's setting, so a `| Path | Purpose |` table followed by a `| Situation | Read |` table makes the sweep read the second table's column-0 labels as candidate link cells. They classify as prose today so nothing breaks, but a label that happens to look path-shaped would be reported as a broken link. Related: the mutant the criterion's own docstring names - initialising `label_cols` empty - survives, because a `| Task | Read |` header re-arms it before any data row.
- **BG0437's recorded measurement does not reproduce and the fragment contradicts its own denominator**: The changelog fragment and the code comment both state 'over the 1438 Raised-by lines in this corpus, 13 write `<id> carry-over`'. No counting method reproduces those figures - two independent passes measured 12 of 1450, invariant across the base ref, the run's head and HEAD. The same fragment then cites 'the measured zero of 1450', contradicting the denominator it gave three lines earlier. Separately, the case-fold the fragment calls 'the half that was already earning its place' is pinned by nothing: dropping IGNORECASE from any of the three patterns leaves all 21 tests green, and the corpus holds no non-lowercase run ids.
- **two readers format token_forecast as an int and crash on the mapping shape a third reader was taught to accept**: `_close_cost` now reads `token_forecast` in both shapes - the plain int the plan writes, and the mapping a later schema may use. Two other readers do not: `_cost_note` and `handoff._appetite_body` both format it directly and raise TypeError on a mapping. Three readers of one field, two of which would crash on the shape the third accepts. Inert today because only the int shape is ever written, which is exactly why it will not be noticed until the schema moves.
- **two readers format token_forecast as an int and crash on the mapping shape a third reader was taught to accept**: `_close_cost` now reads `token_forecast` in both shapes - the plain int the plan writes, and the mapping a later schema may use. Two other readers do not: `_cost_note` and `handoff._appetite_body` both format it directly and raise TypeError on a mapping. Three readers of one field, two of which would crash on the shape the third accepts. Inert today because only the int shape is ever written, which is exactly why it will not be noticed until the schema moves.
- **BG0507's retry half is unprovable in its own fixture, and BG0513's prune test is unfalsifiable**: Two verifiers that pass for the wrong reason. Neither indicates a defect in the code they cover - both mechanisms were independently confirmed working - so this is test debt, filed separately from the criteria that are actually unpinned.

  **BG0507 AC2** demands the retry be demonstrated end to end: collapse, retry, observe the suites execute. The shipped tests assert only that the verdict file is absent. The author closed the chain by running `gate.py --suite-decision` by hand, which is not a test - and the fixture cannot host one, because `--suite-decision` answers `run` inside it regardless of whether a verdict exists (its surface cannot be hashed). So any AC2 test written in that fixture would pass vacuously.

  **BG0513's `test_the_sweep_never_descends_into_an_excluded_directory`** patches `os.walk` to record visited directories. `Path.rglob` uses `os.scandir` and never calls `os.walk`, so under a faithful post-filter mutant the recorder collects nothing and `assertEqual(buried, [])` passes trivially. The naive mutant was killed only incidentally, because `rglob` also yields directories. The prune itself is correct: `_sites()` returns an identical 14-entry set at HEAD and at the base ref.
- **gate.py's suite-reuse branch is disabled by a literal False, and its comment describes a rule the branch above already enforces more strongly**: `gate.py:3170` reads `elif False and recorded_mode != "full":`. The branch is unreachable. Its comment calls it "the coverage half of the boundary rule" and states that a green earned by a partial run must not stand in for a boundary's coverage.

  VERIFIED, because the obvious reading is wrong and I nearly filed it as a live fail-open: the branch immediately above it, `elif at_boundary:` at :3162, refuses reuse at EVERY boundary unconditionally, whatever the recorded mode. So the boundary coverage rule IS enforced, and more strongly than the dead branch would enforce it.

  What enabling the branch would actually do is refuse reuse of a selected-earned green on ORDINARY commits as well - which would make every commit run the full suites and would remove most of the value of selection. That is almost certainly why it was disabled, and the disabling looks deliberate.

  The defect is therefore not coverage loss. It is that a reader cannot tell any of this from the code: the `False` records no reason, the comment describes a rule as though this branch carried it, and nothing says whether the disabling was a decision or an accident left behind. `git log -S 'elif False and recorded_mode'` is the only way to find out, which is the state AGENTS.md's own doctrine says a guard should never be in.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Consolidation opened |
