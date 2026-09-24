# RETRO-0123: RUN-01M39MC0: Sprint 3 of back to basics, commits under ninety seconds and lanes that show their yield

> **Date:** 2026-09-24
> **Batch:** BG0742, BG0754, US0890, US0892, US0893, US0894, US0895, US0896, US0897, US0898, US0899, US0901, US0902, US0903, US0906, US0907, US0908

## Keep

- Deleting lanes rather than tuning them: the warning ratchet, the verify ratchet, the boundary roster and the release-notes count pin are gone, and eight advisory gate lanes left the commit. A one-line gate.py commit fell from 229s to 93s end to end, its suites from 149s to 43s, and most commits this run cleared in 60-75s.
- One QA-seat reviewer per unit, briefed by `critic.py brief`, capped at two rounds: 12 of 20 reviewed units were rejected at round 1 and every finding was real; 8 converged at round 2, 4 were carried with their fixes filed (BG0756, BG0759, BG0760, BG0761), and the run never stopped for any of them.
- Persona seats answering the run's questions: D0262 to D0265 were ruled by seats and none reached the operator. The backlog sweep (D0265) closed 197 items and held 47 open until the deletions they wait on ship (D0264).

## Stop

- Hand-landing each patch: apply, widen Affects, verify, record, transition and commit took six commands per unit, and Affects was widened by hand on nearly every landing because build agents touch tests the story never named. Widening Affects after briefing also invalidates the brief fingerprint, so two verdicts recorded as unmatched.
- Leaving hand-back worktrees behind: 45 agent worktrees hold uncommitted work nobody will land, because agents hand back patches rather than commits.

## Try

- [LC-002] Cited 40 times this run: US0901's scan admitted refusals outside `run`, US0905's AC2 test read one file while a third pin lived in another and then its repair hard-coded lane names of its own, and US0904's fixtures had no same-second retry. Before review, run each criterion's test with the feature removed from a sibling file as well as the named one.
- [LC-008] US0905 set out to retire hand-kept lane pins and twice shipped claiming one pin while another remained: when a unit retires a pin, grep the whole suite for the pinned names before claiming it is gone.
- [new: the review cap carries trivial fixes | review] Two of four carried units (US0904, US0891) were left one line from green. The cap holds, but a round-2 finding should state its fix size, so the carried bug is sized from the review and lands first in the next sprint.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling made on it.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0754 | deferred | Claude Opus 5.5 | 2026-09-24 |
| BG0756 | not-stop-ship | Claude Opus 5.5 | 2026-09-24 |
| BG0757 | not-stop-ship | Claude Opus 5.5 | 2026-09-24 |
| BG0758 | not-stop-ship | Claude Opus 5.5 | 2026-09-24 |
| BG0759 | not-stop-ship | Claude Opus 5.5 | 2026-09-24 |
| BG0760 | not-stop-ship | Claude Opus 5.5 | 2026-09-24 |
| BG0761 | not-stop-ship | Claude Opus 5.5 | 2026-09-24 |
