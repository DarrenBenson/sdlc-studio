# BG1546: install.sh prints the installed banner and exits 0 when every target was skipped or refused

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** install.sh, docs/INSTALL.md, tools/tests/test_install_atomic.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at install.sh install_to() lines 518-540 (`return 0` on the foreign-folder skip and on the refused downgrade) and main() lines 736-768 (`installed_dests` appended unconditionally; `success "SDLC Studio installed for: $targets"`)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:47Z

## Summary

`install_to` in install.sh returns 0 both when it skips a folder that is not a copy of the skill and when it refuses a downgrade of a newer local copy. `main` never learns which targets were written. It adds every requested target to the installed list that the sweep trusts, prints the success banner naming all of them, lists the next steps and exits 0. A run that installed nothing therefore ends by saying SDLC Studio is installed for the target. A script or agent that reads the exit status or the last lines takes the install as done, while the old copy or the foreign folder is what the tool loads. Returning 0 for a single skipped target is a commented choice; the false banner and the unconditional installed list are not.

## Steps to Reproduce

1. Point HOME at a scratch directory and create the folder .claude/skills/sdlc-studio under it holding only a notes.txt file.
2. Run install.sh with --from naming this repository's skill folder, --no-sweep and --target claude.
3. Observed: the warning that the folder is skipped and not touched, then the banner that SDLC Studio is installed for claude with the next steps, exit 0. The folder still holds only notes.txt.
4. Repeat with an existing copy whose version.yaml is stamped 99.0.0. Observed: the refusal to downgrade, then the same banner and exit 0, with version.yaml still at 99.0.0.
5. Expected in both cases: no installed banner, a closing line saying nothing was installed and why, and a non-zero exit.
6. Positive control: an install into an empty scratch HOME prints the banner and exits 0.

## Proposed Fix

Have `install_to` report three outcomes distinctly: installed, skipped and failed. In `main`, add a target to the installed list only when it was written, build the banner and the next steps from that list, and name each skipped target with its reason. When no target was written, print that nothing was installed and exit non-zero; when some were, keep exit 0 and list the skipped ones. The dry run path is unchanged. Extend `test_install_atomic.py` to assert the closing lines and exit status for the foreign folder and the refused downgrade, with a clean install as the control.

## Acceptance Criteria

- [ ] **AC1** Given a scratch HOME whose .claude/skills/sdlc-studio holds only notes.txt, when install.sh runs with `--from` this repository's skill folder, `--no-sweep` and `--target claude`, then no installed banner is printed, the closing line says nothing was installed and why, the exit status is non-zero and notes.txt is untouched. Fails on: 'SDLC Studio installed for: claude' and exit 0 over a skipped foreign folder.
  - **Verify:** pytest tools/tests/test_install_atomic.py::NothingInstalledOutcome::test_a_skipped_foreign_folder_ends_with_no_banner_and_a_failing_exit
- [ ] **AC2** Given an existing copy whose version.yaml is stamped 99.0.0, when the same install runs, then the downgrade is refused, no installed banner is printed, the closing line names the refusal, the exit status is non-zero and version.yaml still reads 99.0.0. Fails on: the banner and exit 0 after a refused downgrade.
  - **Verify:** pytest tools/tests/test_install_atomic.py::NothingInstalledOutcome::test_a_refused_downgrade_ends_with_no_banner_and_a_failing_exit
- [ ] **AC3** Given two targets of which one is written and one is skipped, when install.sh finishes, then it exits 0, the banner and next steps name only the target written, the skipped target is named with its reason, and the list handed to the sweep holds only the written one. Fails on: a skipped target named as installed or trusted by the sweep.
  - **Verify:** pytest tools/tests/test_install_atomic.py::NothingInstalledOutcome::test_a_partly_skipped_run_names_only_what_it_wrote
- [ ] **AC4** Given an empty scratch HOME, when the same install runs, then the banner names the target and the exit status is 0. Fails on: a clean install reported as nothing installed.
  - **Verify:** pytest tools/tests/test_install_atomic.py::NothingInstalledOutcome::test_a_clean_install_still_prints_the_banner_and_exits_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
