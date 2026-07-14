# BG0132: CR acceptance criteria carry Verify lines that nothing executes, so a false-green one is never caught

> **Status:** Fixed
> **Severity:** Medium
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/validate.py
> **Verification depth:** functional - the refusal was exercised through the public CLI (`file_finding.py file --type cr`): a command-shaped `Verify: rg -qi ...` acceptance criterion is refused with a teaching error and no artefact written, while the same CR with an honest prose outcome is accepted and filed. Also covered by 13 behavioural tests, none of which assert a string in a source file.

## Summary

Only STORIES carry canonical executable verifiers (all 377 '**Verify:**' lines in the workspace are on stories). CRs and bugs carry prose ACs - but the convention has been to write a 'Verify: <command>' into that prose, which LOOKS executable and is never run. So a wrong or vacuous check is never detected. Two instances found in one day, both in CRs filed this session: CR0250's Verify grepped for a backticked `REQUIRE_CHECKSUM` when the env var is `SDLC_STUDIO_REQUIRE_CHECKSUM` (could never match - a permanent false RED); CR0257's Verify was 'rg -qi effort sprint.py', which PASSES today on five unrelated prose matches ('agent under effort pressure', 'best-effort') while sprint.py never reads the Effort field at all - a false GREEN on an unbuilt feature. A check nobody runs is not a check, and a check that passes without the feature is worse than none.

## Steps to Reproduce

Read any CR filed this session. Its ACs contain 'Verify: <command>' text. Nothing executes it - `verify_ac` only reads canonical '- **Verify:**' lines on stories. Run CR0257's AC1 command by hand: rg -qi 'effort' sprint.py -> exit 0, though the feature does not exist.

## Proposed Fix

Pick one and make it true. Either (a) STOP writing pseudo-Verify commands into CR/bug AC prose - they are prose checklists, and the executable proof arrives when the CR is actioned into stories; or (b) lint them: a check that any 'Verify:' text in a CR/bug AC is a runnable command and is not trivially satisfiable. (a) is the smaller, honest fix and matches the existing convention. Whichever, the current state - a command-shaped string nobody runs - gives false assurance.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
