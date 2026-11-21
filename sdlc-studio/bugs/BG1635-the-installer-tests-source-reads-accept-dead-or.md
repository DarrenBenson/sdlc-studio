# BG1635: The installer tests' source reads accept dead or inverted install.ps1 guards

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 3
> **Affects:** tools/tests/test_install_uninstall_guard.py, tools/tests/test_install_atomic.py, tools/tests/test_install_requires_pyyaml.py
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T23:35:35Z

## Summary

Run nineteen's qa reviews of US1296, BG1631 and BG1632 (verdicts e7ea95f02955, 24fdef6f3c47, 46a6a321f800, all APPROVE with non-blocking findings) showed the pwsh-less half of each installer test is a regex over install.ps1 that accepts any trailing condition. A guard ending '-gt 0 -and $false' (never fires) or '-gt 0 -or $true' passes at install.ps1:260 and :380, Test-PyYaml can be dead or inverted at :215, and BG1632's banner claim (a run that wrote no target refuses with 'Nothing was installed') is pinned by no executed test on any host: '$installedTargets = @($targets)' at :397 passes. US1296's AC1 test drives only a --from install, so a remote install that skips the PyYAML check passes (mutant at install.sh:755), and AC4's test is a fixed phrase list a paraphrase escapes.

## Steps to Reproduce

In a throwaway copy, change install.ps1:260's guard to end '-gt 0 -and $false' and run tools/tests/`test_install_uninstall_guard.py` on a host without pwsh: green. Repeat for install.ps1:380 with tools/tests/`test_install_atomic.py`, and add '$false -and' before '-not (Test-PyYaml)' at install.ps1:215 with tools/tests/`test_install_requires_pyyaml.py`: green.

## Proposed Fix

Assert each guard's whole condition and that the skip body holds no Copy-Item or Remove-Item. Add a positive control for Test-PyYaml. Drive a remote install (curl and wget stubbed to log) in US1296's AC1 test. Pin BG1632's banner and the Nothing was installed refusal with a non-dry-run executed test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run nineteen's qa reviews of US1296, BG1631 and BG1632 (verdicts e7ea95f02955, 24fdef6f3c47, 46a6a321f800, all APPROVE with non-blocking findings) showed the...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a throwaway copy, change install.ps1:260's guard to end '-gt 0 -and $false' and run tools/tests/`test_install_uninstall_guard.py` on a host without pwsh...
- [ ] **AC3** The proposed fix lands, pinned by a test: Assert each guard's whole condition and that the skip body holds no Copy-Item or Remove-Item.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. install.ps1 guards are correct; only the pwsh-less regex tests would accept a dead guard. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
