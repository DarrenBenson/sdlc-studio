# BG1281: `remote-gate.sh push --release` records an abbreviated sha green, so `release_cut.py tag-check` then refuses the tag it was run for

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_release.py
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg B; repro under scratchpad rel63/legs/scratch-b/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:06:44Z

## Summary

`remote-gate.sh push --commit <sha> --release` accepts an abbreviated sha (the regex allows 7 to 64 hex digits). On a green host run it records that sha unchanged with `release_cut.py record-green`, although the header says '<sha>, in full, recorded green'. `release_cut.tag_check` compares the recorded commit with the tagged commit by exact string equality, so a release gate passed under a short sha is refused at tag time. The refusal tells the operator to re-run the gate, which takes 30 to 60 minutes. The script's own 're-run it on the host' hint echoes the short sha back. No automated caller passes --release, so the operator always types the sha, and `git log --oneline` prints short ones.

## Steps to Reproduce

In a temp-HOME fixture: the parse regex accepts 'faad4b9'. `release_cut.py --root F record-green --commit faad4b9` writes {"commit": "faad4b9"}. `tag_check(F`, <full sha>) returns (False, 'the gate was recorded green on faad4b9, not the commit being tagged (faad4b94a26277e6a8bb96d817dccb05608ad4c8) ... re-run the gate on faad4b9...').

## Proposed Fix

In `cmd_push`, resolve the sha before connecting: resolve it with `git rev-parse --verify <sha>^{commit}` and refuse when that fails. Send and record the full sha. Also consider having record-green itself store `git rev-parse` of its argument.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `remote-gate.sh push --commit <sha> --release` accepts an abbreviated sha (the regex allows 7 to 64 hex digits).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a temp-HOME fixture: the parse regex accepts 'faad4b9'.
- [ ] **AC3** The proposed fix lands, pinned by a test: In `cmd_push`, resolve the sha before connecting: resolve it with `git rev-parse --verify <sha>^{commit}` and refuse when that fails.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-08 | Claude Opus 5.5 | The proposed fix reworded without a command substitution, which the shell-hazard guard refuses in an artefact field |
