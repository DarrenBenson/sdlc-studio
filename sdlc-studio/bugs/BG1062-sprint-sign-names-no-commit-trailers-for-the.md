# BG1062: sprint sign names no commit trailers for the paperwork it writes, so its commit draws one engagement-floor attribution advisory per unit it moved

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_names_its_trailers.py, changelog.d/BG1062.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M4R168 sign commit 2dd360a1, 2026-10-16: the commit-msg hook printed `attribution note (advisory - the commit is not blocked)` with one `engagement floor (attribution)` line for each of the 18 units the sign moved (BG0944, BG0945, BG0950, BG0976, ...).
> **Created:** 2026-10-18
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-18T18:42:25Z

## Summary

`sprint sign` moves every batch unit to its terminal status and tells the operator to commit the result, but never names the `Refs:` trailers that commit needs. The commit-msg hook's engagement-floor attribution then prints an advisory for each staged unit file whose id the message does not name. RUN-01M4R168's sign commit (2dd360a1) drew 18 of them, one per unit moved, and the advisories bury anything else the hook prints.

## Steps to Reproduce

1. `sprint.py sign --report RPTxxxx --principal <operator>` on a run with N units. 2. Commit the paperwork with a message naming the report and one other unit, for example a bug filed in the same commit (`Refs: RPTxxxx`, `Refs: BGxxxx`). 3. The commit hook prints `engagement floor (attribution): this commit stages sdlc-studio/bugs/<id>-....md ... the message never names <id>` N times.

## Proposed Fix

Have `sign` print the trailer block its paperwork commit needs (one `Refs:` per unit it moved, plus the report), or have the attribution lane recognise a commit whose only change to a unit file is the sign's terminal move.

## Acceptance Criteria

- [ ] **AC1** After `sprint sign`, committing its paperwork with the trailers the sign printed draws no engagement-floor attribution advisory for a unit the sign moved
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_names_its_trailers.py -k sign_trailers_satisfy_attribution

## Impact

Advisory noise on every sign commit, proportional to batch size; a real attribution gap in the same commit is easy to miss.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-18 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
