# CR-0719: State Windows support for the script tier in the TSD and either test it or declare it out of scope

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/tsd.md, .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, tsd lens, survived 3 of 3 refute votes; observed at sdlc-studio/tsd.md Scope (lines 65-94), Manual Testing (lines 580-581), CI jobs table row `windows-smoke` (line 683); .github/workflows/lint.yml job `windows-smoke`; .claude/skills/sdlc-studio/scripts/verify_ac.py lines 2491-2493; mutation.py lines 1012-1014
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:33Z

## Summary

The README offers a Windows install and the code carries deliberate Windows branches, so Windows is a supported platform in practice. The only Windows coverage in `sdlc-studio/tsd.md` (lines 580 to 581 and the `windows-smoke` row at line 683) is the installer smoke job in `.github/workflows/lint.yml`, which proves files are placed and runs no Python. The whole script tier runs only on Linux in CI and at the push, and the TSD neither gates Windows nor lists it as out of scope or a known gap. By reading the source, two paths would raise on Windows: the group kill in the phase runner of `verify_ac.py` (lines 2491 to 2493) and in `reap` in `mutation.py` (lines 1012 to 1014) call `os.killpg` with `signal.SIGKILL`, neither of which exists there, inside a suppression that does not catch the resulting AttributeError. The id-allocation lock in `sdlc_md.py` also silently becomes no lock where `fcntl` is missing. The source reading was not executed on a Windows host.

## Impact

A Windows user installs a product whose scripts have never been run on their platform by any gate. Acceptance-criteria verification and mutation runs are likely to fail with an unhandled error in a cleanup path, and concurrent id allocation has no lock, so two agents can mint the same id. Maintainers cannot tell from the TSD or the PRD whether a Windows defect is a regression or an unsupported case.

## Acceptance Criteria

- [ ] The TSD states which platforms the script tier is supported on and, for Windows, either the gate that runs it or an explicit out-of-scope or known-gap entry.
- [ ] If Windows is supported, the `windows-smoke` job runs at least a named subset of the script tests with Python on the Windows runner and fails the job when one fails.
- [ ] The group-kill cleanup in `verify_ac.py` and `mutation.py` does not raise where `os.killpg` or `signal.SIGKILL` is absent, held by a test in each script's test module that removes those attributes and runs the cleanup path.
- [ ] Where the id-allocation lock degrades to no lock, the TSD records it as a stated limit of that platform and does not claim every shared write is serialised there.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
