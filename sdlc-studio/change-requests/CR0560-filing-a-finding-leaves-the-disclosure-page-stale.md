# CR-0560: filing a finding leaves the disclosure page stale, so the tree is red until somebody separately remembers to regenerate it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** enhancement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, tools/known_issues.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, tools/tests/test_known_issues.py
> **Evidence:** Hit three times on 2026-08-26 during RUN-01M0YXN3 - filing BG0620, BG0621 and BG0623 - each leaving the tree red on the same three assertions until the page was regenerated and the notes' count hand-corrected.
> **Date:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`file_finding.py file` writes the artefact and its index row but does not regenerate `docs/known-issues.md`, which is derived from the same corpus. `test_known_issues.py` then goes RED on three assertions at once - the new finding is undisclosed, the page is not byte-identical to what the generator produces, and the release notes state a count the corpus contradicts - until somebody runs `python3 tools/known_issues.py --write` and hand-edits the notes' count. This happened THREE times in one session on 2026-08-26, filing BG0620, BG0621 and BG0623, each time leaving the working tree red between the filing and the remedy. The guard is doing its job; the gap is that the deterministic creator leaves a derived surface behind.

## Impact

It converts a one-step action into a three-step one, and the two extra steps are invisible until a test run. An agent or a contributor who files a finding and commits - which is the whole point of `file_finding.py` - hits a refusal about a page they did not touch and a count they did not write. It also trains people to treat a red `test_known_issues` as noise, which is the lane that guards the release bar.

## Acceptance Criteria

- [ ] Given a Medium or Low finding is filed, when the filer returns, then `docs/known-issues.md` already discloses it - the page is derived from the corpus the filer just wrote to, so leaving it stale makes the creator the thing that breaks the guard
- [ ] Given a finding is filed at a BARRED severity, when the filer returns, then the disclosure page is unchanged and the release-notes count is unchanged - the paired control, since High and Critical are barred rather than disclosed and must not silently enter the residue
- [ ] Given the release notes state a disclosed count, when a finding is filed or closed, then that count is derived rather than hand-edited - it is the one number in the notes that tracks the corpus, and it has been corrected by hand on every filing this session

## Steps to Reproduce

1. `file_finding.py file --type bug ...` for any Medium or Low finding. 2. `python3 -m pytest tools/tests/test_known_issues.py`. 3. Three failures, none of them about the finding itself. 4. `python3 tools/known_issues.py --write`, then edit the disclosed count in docs/release-notes-v5.0.1.md by hand, and they pass.

## Proposed Fix

Have the filer regenerate the derived page as part of writing the finding, the way `artifact.py new` already wires the index row - a derived surface is exactly what a deterministic creator should own. The notes' COUNT is derived too and is currently hand-edited on every filing, so it should either be generated into a marked span or the guard should read the number from the page rather than from prose. If regenerating on every filing is unwanted, the filer should at least PRINT the one command that clears what it just broke.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Raised |
