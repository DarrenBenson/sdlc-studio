# BG0593: close --dry-run previews against a scratch tree with no git, so every git-reading row degrades to unjudged

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`close_dry_run` copies only `root/sdlc-studio` into a temp directory and runs the chain steps against it, so the scratch tree has no `.git`. Every checklist resolver that reads git therefore answers as if the repository were unreadable: `_ck_tick_verification` returns `diff unreadable` where a real close would report ticked criteria the tree does not support. A preview that softens a refusal into `unjudged` is the one way a preview actively misleads, and this module's own docstring says it exists so that an operator can see every refusal in one pass before paying for a close.

## Steps to Reproduce

Measured 2026-08-18 at e2cafa72, and it is the diagnosis of an observation parked as undiagnosed in BG0584. `sprint.py` line 7074 runs `shutil.copytree(root / 'sdlc-studio', scratch / 'sdlc-studio', symlinks=True)` and nothing else. Executed against the run's own recorded base ref ba3bffa2c: `sprint_report._changed_paths(Path('.'), base)` returns 64 paths; the same call against the scratch root returns None; `(scratch / '.git').exists()` is False. That is the whole of the 'same row resolved two different ways within one invocation' that BG0584 records - `close_preflight` runs against the REAL root and answers `no ticked criteria found`, while the chain step runs against the scratch and answers `diff unreadable`. Two answers, one invocation, and neither the operator nor the row can tell which tree produced which.

## Proposed Fix

Give the scratch a readable git context, or make the absence explicit rather than silent. The cheap correct shape is to pass the REAL repository root to the resolvers that read history while keeping every WRITE bound to the scratch - the copy exists to protect the tree from writes, not to hide its history. If that separation is awkward, the resolvers must distinguish `no git here` from `diff unreadable` and the dry run must say which, because a preview that reports a softer verdict than the close it previews is worse than no preview. Check every CHECKLIST resolver that touches git, not only tick-verification: the same blindness applies to each, and fixing one leaves the siblings lying.

## Acceptance Criteria

- [ ] **AC1** Given a dry run over a repository whose base ref resolves, when EVERY checklist step resolves, then each returns the same verdict against the scratch root as against the real root, and any step whose verdicts differ is named - the general form, because the scratch copies only `sdlc-studio/` and every probe reading `.claude/skills/`, `tools/` or `changelog.d/` degrades the same way
- [ ] **AC2** Given a tree with genuinely no git history, when a git-reading step resolves under a dry run, then it reports that condition distinctly from `the diff could not be taken` - and the distinction is made where the dry run builds its root, so the resolver it feeds is unchanged and stays available as an independent witness
- [ ] **AC3** Given a dry run, when it completes, then the real tree has still never been opened for writing - the property the scratch copy exists for must survive the fix
- [ ] **AC4** Given a checklist step that reads only `sdlc-studio/`, when the AC1 comparison runs today on the unrepaired tree, then that step already agrees across both roots while the git-reading step does not - the control proving the comparison discriminates rather than passing everything

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, revert the scratch root to a copy of `sdlc-studio/` alone | Given a dry run over a repository whose base ref resolves, when EVERY checklist step resolves, then each returns the same verdict against the scratch root as against the real root, and any step whose verdicts differ is named - the general form, because the scratch copies only `sdlc-studio/` and every probe reading `.claude/skills/`, `tools/` or `changelog.d/` degrades the same way |
| AC2 | in `sprint.py`, delete the branch separating an absent repository from an unreadable one | Given a tree with genuinely no git history, when a git-reading step resolves under a dry run, then it reports that condition distinctly from `the diff could not be taken` - and the distinction is made where the dry run builds its root, so the resolver it feeds is unchanged and stays available as an independent witness |
| AC3 | in `sprint.py`, change the dry-run root to the live working tree | Given a dry run, when it completes, then the real tree has still never been opened for writing - the property the scratch copy exists for must survive the fix |
| AC4 | in `sprint.py`, hard-code every comparison result to agree | Given a checklist step that reads only `sdlc-studio/`, when the AC1 comparison runs today on the unrepaired tree, then that step already agrees across both roots while the git-reading step does not - the control proving the comparison discriminates rather than passing everything |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-18 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Criteria re-pointed by adversarial goal review: evidence taken outside the instrument under repair, and the enumerated case generalised to its class |
