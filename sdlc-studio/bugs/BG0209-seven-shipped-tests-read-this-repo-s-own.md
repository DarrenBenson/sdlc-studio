# BG0209: seven shipped tests read this repo's own story files, so the payload cannot pass its own suite anywhere else

> **Status:** Fixed
> **Verification depth:** functional (run from a simulated installed copy: 7 errors before, 7 clean skips after; dev repo still runs all 144)
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`test_verify_ac` carries DuplicateVerifierTests and US0166Ac3Tests, which open artefacts from the dogfooded workspace by path - sdlc-studio/stories/US0166-... and US0163. Inside the dev repo they pass. Installed at ~/.claude/skills/sdlc-studio, the root walk lands on the home directory, the files are absent, and all seven raise FileNotFoundError. A consuming project that runs the shipped suite therefore sees seven errors that say nothing about its own install. Other workspace-coupled tests in the same run skip cleanly (7 skipped), so the pattern is established and these seven are the exceptions. The skill is functionally healthy either way: 3,166 of 3,173 pass in the installed copy and the failures are all missing-fixture, not logic. Found by verifying the forward-port rather than trusting that it applied.

## Steps to Reproduce

1. bash tools/forward-port.sh --yes. 2. cd ~/.claude/skills/sdlc-studio/scripts. 3. python3 -m unittest discover -s tests. 4. Observe FAILED (errors=7, skipped=7), every error a FileNotFoundError on a dev-repo story path.

## Proposed Fix

Make the seven skip when the artefact they read is absent, the way the other workspace-coupled tests already do - a guard that resolves the story path and calls skipTest when it does not exist. Alternatively hold them out of the shipped payload as repo-only tests, the way tools/tests is held out. Skipping is preferable: the assertions are still useful inside the dev repo.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
