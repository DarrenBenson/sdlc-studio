# EP0262: Commits clear in ninety seconds, and every constraint earns its place

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Sprint 3 of the back-to-basics programme, part one. Makes a code commit clear inside the 90-second budget from measured causes (the uncached decisions scan, sequential pre-commit lanes, xdist chunking, live-repo tests per commit, the quadratic `close_owed` walk), deletes the ratchet mechanisms that caught no code defect (warning and verify ratchets, hand-pinned release notes, refused index drift, CR filing refusals, prose pins on AGENTS.md, advisory lanes per commit), and adds a lean counterweight: lesson graduation retires rather than adds, refusal yield is measured, the commit lane count is capped, and the persona seats watch for the ratchet. Also sweeps the backlog against the lean direction and fixes the Python 3.10 floor.

## Story Breakdown

- [x] [US0890: Recording a waiver no longer re-reads every script](../stories/US0890-recording-a-waiver-no-longer-re-reads-every.md)
- [ ] [US0891: A commit's pre-commit lanes run side by side](../stories/US0891-a-commit-s-pre-commit-lanes-run-side.md)
- [x] [US0892: A commit's selected tests are handed out one at a time across every worker](../stories/US0892-a-commit-s-selected-tests-are-handed-out.md)
- [ ] [US0893: A commit leaves the live-repository tests to the push](../stories/US0893-a-commit-leaves-the-live-repository-tests-to.md)
- [x] [US0894: The close-owed report walks the corpus once, not once per epic](../stories/US0894-the-close-owed-report-walks-the-corpus-once.md)
- [ ] [US0895: A commit runs only the gate lanes that can refuse it](../stories/US0895-a-commit-runs-only-the-gate-lanes-that.md)
- [x] [US0896: Footprint warnings advise, and a finished artefact is never re-judged](../stories/US0896-footprint-warnings-advise-and-a-finished-artefact-is.md)
- [x] [US0897: A shared Verify selector is an advisory note within one artefact, never a commit refusal](../stories/US0897-a-shared-verify-selector-is-an-advisory-note.md)
- [x] [US0898: A shipped release's notes stay as shipped, and the defect count is written at the cut](../stories/US0898-a-shipped-release-s-notes-stay-as-shipped.md)
- [ ] [US0899: Mechanical index and epic drift is fixed at commit, not refused](../stories/US0899-mechanical-index-and-epic-drift-is-fixed-at.md)
- [ ] [US0900: A change request can be filed before it is sized](../stories/US0900-a-change-request-can-be-filed-before-it.md)
- [ ] [US0901: The hooks list their own lanes, and AGENTS.md stops restating them](../stories/US0901-the-hooks-list-their-own-lanes-and-agents.md)
- [x] [US0902: Adding a script no longer needs a matching TSD sentence to commit](../stories/US0902-adding-a-script-no-longer-needs-a-matching.md)
- [x] [US0903: A recurring lesson asks for a fix or a retirement, not another check](../stories/US0903-a-recurring-lesson-asks-for-a-fix-or.md)
- [ ] [US0904: Each lane's refusals are counted against the defects they caught](../stories/US0904-each-lane-s-refusals-are-counted-against-the.md)
- [ ] [US0905: Adding a commit lane means removing one](../stories/US0905-adding-a-commit-lane-means-removing-one.md)
- [x] [US0906: The review seats push back on a check that earns nothing](../stories/US0906-the-review-seats-push-back-on-a-check.md)
- [ ] [US0907: The backlog holds only the work the lean direction still wants](../stories/US0907-the-backlog-holds-only-the-work-the-lean.md)
- [x] [US0908: The skill's scripts run on the Python 3.10 it declares](../stories/US0908-the-skill-s-scripts-run-on-the-python.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
