# BG1640: install.sh's sidecar refusals for an empty body, a transport fault and wget are unpinned

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_install_sidecar_fault.py, install.ps1
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T00:14:21Z

## Summary

BG1543's qa review (verdict 5e97c24528fa-c9268e4f, RUN-01M7TTK3, non-blocking) found three gaps in tools/tests/`test_install_sidecar_fault.py.` A 2xx sidecar with an empty body on the fallback (install.sh:432) refuses, but the mutant that reads it as an absence survives. The mutant 'return 1' to 'return 22' on curl's transport branch (install.sh:391) survives the whole install suite, and against a connection reset on the fallback's sidecar it installs unverified with exit 0. The wget branch's status naming (install.sh:401-403) runs in no test, so the changelog's 'curl's or wget's exit code' is unverified for wget. Also the AC1 loop's assertIn on server.hits (`test_install_sidecar_fault.py`:138) cannot fail after the first subtest, because hits accumulate.

BG1543's round-two reviews (verdicts 4a817a541727-877d4b34 and 4a817a541727-ace376c4) add install.ps1 gaps: the empty-sidecar throw and the `$code` derivation (`$code = $null` at install.ps1:338) are pinned by no test, the test's PowerShell condition reader gets `-not` precedence wrong, and the comment at install.ps1:322 is stale.

## Steps to Reproduce

In a throwaway copy, change install.sh:391's 'return 1' to 'return 22' and run tools/tests/`test_install_sidecar_fault.py`: green. Then serve a connection reset on the fallback's sidecar: the install exits 0 unverified.

## Proposed Fix

Add cases for an empty 2xx body and a connection reset on the fallback's sidecar, drive the wget branch with a stub wget on PATH, and reset server.hits per subtest.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1543's qa review (verdict 5e97c24528fa-c9268e4f, RUN-01M7TTK3, non-blocking) found three gaps in tools/tests/`test_install_sidecar_fault.py.` A 2xx sidecar...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a throwaway copy, change install.sh:391's 'return 1' to 'return 22' and run tools/tests/`test_install_sidecar_fault.py`: green.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add cases for an empty 2xx body and a connection reset on the fallback's sidecar, drive the wget branch with a stub wget on PATH, and reset server.hits per...

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. install.sh refusals behave as intended; only mutants and the wget branch lack tests. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
