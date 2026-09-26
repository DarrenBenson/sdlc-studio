# RETRO-0125: RUN-01M3CK1K Sprint 5: the lean loop runs on a fresh v6 project and the release candidate is prepared

> **Date:** 2026-09-26
> **Batch:** BG0681, BG0687, BG0695, BG0711, BG0717, BG0731, BG0771, BG0772, BG0773, BG0775, BG0777, BG0778, BG0779, BG0780, BG0781, US0914, US0918, US0919, US0922, US0923, US0925, US0936, US0937, US0938, US0939, US0940, US0942, US0943, US0944, US0945, US0946, US0947, US0948, US0949, US0950, US0951

## Keep

- One QA-seat reviewer per unit, capped at two rounds, with round 2 judging the repair against round 1's findings: 16 units were rejected at round 1, 15 converged at round 2, and US0941 was carried as BG0775 and landed in the same run. Every round-1 REJECT named a defect a mutant proved - a signed-report forgery route, five shipping review rules left untested by a deletion, a leak guard the flake fix dropped - not wording.
- Filing what a review finds instead of widening the unit: ten follow-up bugs (BG0777-BG0786) were filed, and the ones a v6 user would meet (v3 ids in the retro, lock errors, the hook hiding the re-read advisory) were groomed and landed in the same run.
- Collapsing the review record to one verdict ledger: the repair ledger, the sign-off verbs, the evidence and sprint-review verbs, the mutation ledger verbs and the brief-provenance refusal are gone, each retired criterion recorded in the D0259 pattern and the historic record read frozen rather than rewritten.

## Stop

- Widening a unit's Affects after its reviewer was briefed: US0944, US0919 and US0942 left verdict rows marked unmatched. A fix round that touches a new file needs a re-brief before the reviewer sees it.
- Deleting a test class whole when some of its tests pin behaviour that still ships: US0918 dropped the only tests of five live review rules, as US0917 did the sprint before.
- Running up to seven agents at once: the account's spend cap stopped the run twice mid-work, and four agents kept the loop just as busy.

## Try

- [LC-002] Before a deletion unit hands back, mutate each rule the deleted tests pinned and confirm a surviving test still kills it; re-home the test before retiring the stamp.
- [new: widen-after-brief | review] A review judges the scope it was briefed on, so a unit whose Affects grows after the brief is judged against the wrong scope. Before sending a fix round to its reviewer, re-brief the unit whenever its file changed since the last brief.
- [new: a reviewer's clone cannot see writes into the main repo | review] A full suite run in a scratch clone cannot see a test that writes into the main repository, as US0951's run-state write showed. Treat the commit gate's repo-writes lane as the arbiter of repo writes, and never read a reviewer's green clone run as proof that none happen.
