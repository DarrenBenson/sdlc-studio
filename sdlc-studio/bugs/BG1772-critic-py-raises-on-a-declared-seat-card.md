# BG1772: critic.py raises on a declared seat card that is not valid UTF-8, so recording a verdict fails with a traceback

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_declared_reviewers_bad_card.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1772.md
> **Evidence:** run twenty-eight, BG1764's round-three review: the qa seat found critic.py raises identically at base 15136cad5 ([pre-existing]); BG1767 tracked it only until BG1764's carry closed
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** orchestrator; agent; claude-opus-5-5
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-26T09:35:52Z

## Summary

`critic._declared_reviewers` reads each seat card with `read_text(encoding="utf-8")` and catches only OSError, so a card under personas/seats or personas/amigos that is not valid UTF-8 raises UnicodeDecodeError out of every command that resolves the declared seats, among them `critic.py record`. The cost anatomy no longer crashes on such a card (it falls back to the shipped seats), but the review commands still do. Same class as the crash fixed for the anatomy.

## Steps to Reproduce

In a fixture project, write `sdlc-studio/personas/seats/bad.md` holding the bytes `\xff\xfe` plus a valid header, then run `python3 .claude/skills/sdlc-studio/scripts/critic.py record --unit US0001 --verdict approve --reviewer 'x (qa)' --author 'y (engineering)'`; it exits 1 with a UnicodeDecodeError traceback.

## Proposed Fix

Catch UnicodeDecodeError (as a ValueError) beside OSError in `_declared_reviewers`, skip the unreadable card with a one-line warning naming it, and keep reading the valid cards beside it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `critic._declared_reviewers` reads each seat card with `read_text(encoding="utf-8")` and catches only OSError, so a card under personas/seats or...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a fixture project, write `sdlc-studio/personas/seats/bad.md` holding the bytes `\xff\xfe` plus a valid header, then run `python3...
- [ ] **AC3** The proposed fix lands, pinned by a test: Catch UnicodeDecodeError (as a ValueError) beside OSError in `_declared_reviewers`, skip the unreadable card with a one-line warning naming it, and keep...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | orchestrator | Filed |
