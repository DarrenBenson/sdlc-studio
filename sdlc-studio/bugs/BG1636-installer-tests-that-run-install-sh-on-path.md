# BG1636: Installer tests that run install.sh on PATH=/usr/bin:/bin fail where the system python3 cannot import yaml

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_install_gemini_hint.py, tools/tests/test_install_atomic.py, tools/tests/test_lean_consumer_files_preserved.py
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T23:35:57Z

## Summary

US1296 made install.sh refuse without PyYAML. Tests that run a real install.sh with a curated PATH=/usr/bin:/bin (tools/tests/`test_install_gemini_hint.py`:19 `BASE_PATH`, tools/tests/`test_install_atomic.py`:248, `test_lean_consumer_files_preserved)` now depend on /usr/bin/python3 importing yaml. With a stub python3 that cannot, `test_install_gemini_hint` went from 2 passed at af90be96 to 2 failed. CI's lint.yml installs it, but nothing names the prerequisite for a developer host or the gate host. Found by US1296's qa review (verdict e7ea95f02955-0c5ce244, non-blocking, RUN-01M7TTK3).

## Steps to Reproduce

Put a python3 stub that raises ImportError on 'import yaml' ahead of /usr/bin on `test_install_gemini_hint.py`'s `BASE_PATH` and run the module: 2 failed.

## Proposed Fix

Give each curated-PATH installer test the python3 wrapper `test_install_copilot_global.py` uses, pointing at the running interpreter, so the test no longer depends on the host's system python3.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1296 made install.sh refuse without PyYAML.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Put a python3 stub that raises ImportError on 'import yaml' ahead of /usr/bin on `test_install_gemini_hint.py`'s `BASE_PATH` and run the module: 2 failed.
- [ ] **AC3** The proposed fix lands, pinned by a test: Give each curated-PATH installer test the python3 wrapper `test_install_copilot_global.py` uses, pointing at the running interpreter, so the test no longer...

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it needs a condition no real install meets. Installer tests on PATH=/usr/bin:/bin fail only where the system python3 lacks yaml; install.sh refusing without PyYAML is intended. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
