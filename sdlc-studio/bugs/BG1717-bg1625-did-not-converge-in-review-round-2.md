# BG1717: BG1625 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1625.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_kept_list.py
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T23:12:37Z

## Summary

BG1625 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] `pytest_targets` keeps the `=` of a short option's attached value (critic.py:3092), so a Verify line `pytest tests/test_widget.py -rA -k=add` is named through `critic.py brief` as "(-k =add filters by expression and names no test ...)". pytest reads `-k=add` as the expression `add`: `pytest --co -q -k=add` collected 1 of 2 tests in a fixture (pytest 9.1.1, Python 3.14). The repair's docstring says a short option word "is a cluster read as pytest's argparse reads it" (critic.py:3069), and its commit message says it "reads a cluster of short flags as pytest's argparse does". Both are FALSE for this form, and the printed expression is not the one pytest runs. No selector is printed wrong, so AC1 itself holds. Drop the `=` that directly follows the option letter, as argparse does, and add the case to `test_a_cluster_of_short_flags_is_read_as_pytest_reads_it` [LC-018]; RULINGS: Round one's first finding ("`pytest_targets` (critic.py:3048-3071) still names an expression's words") is CLOSED. Through `critic.py brief` in a throwaway project, `-qk 'add or sign'`, `-vm 'slow and not flaky'`, `-r a -k add`, `-p no:cacheprovider -W error` with `--deselect`, and `-n 4 --dist loadfile -k add` each name only `tests/test_widget.py`, with the expression named as one that names no test. Its second finding ("Three behaviours the diff adds have no test") is CLOSED. Re-run alone, `exprs += expressions` fails `test_an_expression_named_twice_is_named_once`, narrowing the catch to `ValueError` fails `test_a_kept_list_that_cannot_be_read_is_refused_by_name` (IsADirectoryError), and the unresolved root fails both `_kept_report_path` subtests (`.` and the symlink). Verify dry-run passes 3 of 3, and the author's 9 recorded mutants replay killed. My mutants killed: the attached value ignored, the empty-value guard dropped, `-n` dropped from the list, and `-r` dropped against the brief test alone. One survivor, long options read as clusters, is equivalent for every flag of the installed pytest except `--help` (probed against its parser). Claim inventory: the `_PYTEST_VALUE_OPTIONS` comment is TRUE (with plugins autoloaded, pytest 9.1.1 and pytest-xdist 3.8.0 read one value for no option the list lacks). The changelog's new sentence is TRUE by the CLI probes. The commit message's "the CLI hands the record a root it has already resolved" is TRUE (`sdlc_md.resolve_root`). The argparse sentence is FALSE for an attached `=` (ISSUES). Remark: `test_every_option_pytest_reads_a_value_for_is_listed` goes red when an upgraded pytest adds a value option, which its docstring intends. The suites over test\_critic.py, test\_critic\_self\_check\_kept\_list.py, test\_critic\_self\_check\_record.py, test\_precommit\_unrecorded\_verdict.py and test\_lean\_commit\_lanes.py pass in a detached worktree (268 passed). Re-ran: my first worktree was written into by another reviewer's run from 22:54 to 22:55 UTC. Every BG1625 run was taken after 22:58 in a fresh worktree that showed clean after each mutant and again at 23:08 UTC, and the two mutants run after that check were killed. This verdict rests only on runs in that worktree.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1625 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1625 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] `pytest_targets` keeps the `=` of a short option's attached value (critic.py:3092), so a Verify line `pytest tests/test_widget.py -rA -k=add` is named through `critic.py brief` as "(-k =add filters by expression and names no test ...)". pytest reads `-k=add` as the expression `add`: `pytest --co -q -k=add` collected 1 of 2 tests in a fixture (pytest 9.1.1, Python 3.14). The repair's docstring says a short option word "is a cluster read as pytest's argparse reads it" (critic.py:3069), and its commit message says it "reads a cluster of short flags as pytest's argparse does". Both are FALSE for this form, and the printed expression is not the one pytest runs. No selector is printed wrong, so AC1 itself holds. Drop the `=` that directly follows the option letter, as argparse does, and add the case to `test_a_cluster_of_short_flags_is_read_as_pytest_reads_it` [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1625 AC1 still passes: Given a Verify line using `-k 'a or b'`, when `critic.py brief` prints the replay of the author's mutants, then it prints the real selected tests or refuses the expression by name, never ids such as `a` and `b` as selectors. Fails on: bogus selectors printed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_kept_list.py::CriticReplaySelectorTests
- [ ] **AC3** BG1625 AC2 still passes: Given a read-only sdlc-studio/reviews/author-mutants/ directory, when `critic.py self-check record --mutants-from <report>` runs, then it exits non-zero saying the kept list was not written and adds no self-check row; a malformed kept list is refused with a named error, not a crash. Fails on: the row added while the message says nothing was written, and a malformed kept list crashing the brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_kept_list.py::CriticKeptListWriteTests
- [ ] **AC4** BG1625 AC3 still passes: Given a kept list written for a unit, when its file is read, then it holds a path relative to the repository root, and a report of the wrong kind or version is refused. Fails on: an absolute local path in a committed file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_kept_list.py::CriticKeptListPathTests

- [ ] **AC5** The round 3 REJECT finding no longer holds: an attached value holding an `=` that is not directly after the option letter is read whole, pinned by a case such as `-m'device(serial=1)'` and its cluster `-qm'device(serial=1)'` in `test_a_cluster_of_short_flags_is_read_as_pytest_reads_it`; the mutant that splits at the first `=` (`attached.partition("=")[2]`) fails it (critic.py:3072, 3095-3096; verdict aa5575a8c536-f9c40d5c, D0591).
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC6** The round 3 REJECT finding no longer holds: `changelog.d/BG1625.md` states exactly how a value joined to its option by `=` is read, including the Python 3.10 difference for a cluster such as `-qk=add`, which argparse on 3.10 keeps as `=add`.
  - **Verify:** manual - the independent review of the redelivery re-checks this finding

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-two orchestrator) | BG1625's ruled round three (D0591) closed AC1's finding and rejected for an unpinned `=` case and a fragment false on Python 3.10; two criteria carry them to the next run |
