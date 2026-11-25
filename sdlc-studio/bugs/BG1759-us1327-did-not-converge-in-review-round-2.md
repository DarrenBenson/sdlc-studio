# BG1759: US1327 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** docs/release-notes-v6.5.0.md, tools/tests/test_lean_release_notes_v65.py, changelog.d/US1327.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-25T20:29:44Z

## Summary

US1327 was rejected at round 2, the review cap, by agent-a221a2fa74b4e4a5f (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the repair's `ruled_at` is unpinned: the commit it picks can be replaced by HEAD with the suite green (tools/tests/test\_lean\_release\_notes\_v65.py:292-302, the subtest at :873-896). The mutant `return commits[0]` to `return "HEAD"`, applied once in a detached worktree at 774cdfa48 with `__pycache__` purged, left test\_the\_quality\_figures\_name\_their\_decisions green (1 passed, 1 subtest passed). The subtest's control patches only `BUGS`, and today the committed corpus at HEAD matches the ruled one. The mutant is not equivalent. In a throwaway clone with one later commit setting BG0971 to Open, the unmutated test passed and the mutant failed at :876 with "the bug corpus holds 127 bugs at Won't Fix under D0613, where the notes say 128". That is the round-one failure coming back through a reader of the committed tree. Pin the commit itself, for example by asserting that the decisions log at `ruled_at(dec)` holds the row and its parent does not (a missing pin under D0561); RULINGS: Round one, finding 1 ("the AC2 Won't Fix counts are read from the live bug corpus"): CLOSED. Re-probed in a detached worktree at 774cdfa48 with BG0971 set to Open and a later Won't Fix bug citing D0564 added: test\_the\_quality\_figures\_name\_their\_decisions passed (1 passed, 1 subtest). `ruled_at` names 622cb4156 and e8bed39a5. These are the commits whose subjects close 139 and 128 Low bugs as Won't Fix under D0564 and D0613, and they touch 141 and 138 bug files. The mutant that reads the working tree (`wont_fix(Path(d))` to `wont_fix()`) now fails it, and so does the mutant that drops the corpus comparison in quality\_problems. Round one, finding 2 ("the upgrade text check that the dry run"): CLOSED. The `if False:` mutant now fails test\_the\_64\_upgrade\_path\_is\_given (1 failed). Claim inventory of the repair: the fragment's new sentence is TRUE, because the unmutated test passes after a later commit reopens BG0971 in a throwaway clone. The docstring says the subtest is skipped outside a clone, and that matches needs\_cli. This repair does not change the notes page. Its count line moved to 46 open, 0 Medium, 46 Low in 4841d946b (US1331), which is outside this unit. `verify_ac.py run --id US1327 --dry-run` at 774cdfa48 reports ac=6 pass=6. Cost: the AC2 test now runs one git show per bug file. It took 11 to 22 s here, against about 2 s at round one, and the module took 65 s. This is not a finding.

## Steps to Reproduce

1. Read the round 2 REJECT of US1327 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1327 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the repair's `ruled_at` is unpinned: the commit it picks can be replaced by HEAD with the suite green (tools/tests/test\_lean\_release\_notes\_v65.py:292-302, the subtest at :873-896). The mutant `return commits[0]` to `return "HEAD"`, applied once in a detached worktree at 774cdfa48 with `__pycache__` purged, left test\_the\_quality\_figures\_name\_their\_decisions green (1 passed, 1 subtest passed). The subtest's control patches only `BUGS`, and today the committed corpus at HEAD matches the ruled one. The mutant is not equivalent. In a throwaway clone with one later commit setting BG0971 to Open, the unmutated test passed and the mutant failed at :876 with "the bug corpus holds 127 bugs at Won't Fix under D0613, where the notes say 128". That is the round-one failure coming back through a reader of the committed tree. Pin the commit itself, for example by asserting that the decisions log at `ruled_at(dec)` holds the row and its parent does not (a missing pin under D0561)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** US1327 AC1 still passes: Given docs/release-notes-v6.5.0.md, then it opens with a one-sentence headline naming
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you
- [ ] **AC3** US1327 AC2 still passes: Given the quality theme, then it states D0560's bar (fewer than 50 open defects and none
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_quality_figures_name_their_decisions
- [ ] **AC4** US1327 AC3 still passes: Given the notes' section on changed behaviour, then it names each change a 6.4 user
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do
- [ ] **AC5** US1327 AC4 still passes: Given the notes' 'Upgrading from 6.4' section, then it says to install PyYAML
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_the_64_upgrade_path_is_given
- [ ] **AC6** US1327 AC5 still passes: Given every cost figure the notes state (priced tokens, dollars, dollars per point or
  - **Verify:** pytest tools/tests/test_lean_release_notes_v65.py::ReleaseNotesTests::test_every_cost_figure_names_its_signed_report
- [ ] **AC7** US1327 AC6 still passes: Given the notes, then `tools/check_links.py` and `tools/lint-style.sh` pass and the notes
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && test "$(grep -cE '^\*\*v6\.5\.0 discloses [0-9]+ open defects: [0-9]+ Medium, [0-9]+ Low\.\*\*$' docs/release-notes-v6.5.0.md)" = 1

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
